from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI
import google.generativeai as genai
from app.core.config import settings
from app.models.qa import Question, Answer
from app.schemas.qa import QuestionCreate, AnswerCreate, AskRequest, AskResponse

# Initialize clients
# If the key starts with "AIzaSy" or "AQ.", we use the official Google Generative AI SDK directly.
use_gemini_sdk = False
openai_client = None

if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip() and settings.OPENAI_API_KEY != "your-openai-api-key-here":
    key_str = settings.OPENAI_API_KEY.strip()
    if key_str.startswith("AIzaSy") or key_str.startswith("AQ."):
        use_gemini_sdk = True
        genai.configure(api_key=key_str)
    else:
        client_kwargs = {"api_key": key_str}
        if settings.OPENAI_BASE_URL and settings.OPENAI_BASE_URL.strip():
            client_kwargs["base_url"] = settings.OPENAI_BASE_URL
        openai_client = AsyncOpenAI(**client_kwargs)

class QAService:
    @staticmethod
    async def create_question(db: AsyncSession, schema: QuestionCreate) -> Question:
        """
        Creates a new question in the database.
        """
        db_question = Question(text=schema.text)
        db.add(db_question)
        await db.commit()
        await db.refresh(db_question)
        return db_question

    @staticmethod
    async def get_question(db: AsyncSession, question_id: int) -> Optional[Question]:
        """
        Retrieves a single question by its ID.
        """
        stmt = select(Question).where(Question.id == question_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_questions(db: AsyncSession, skip: int = 0, limit: int = 10) -> List[Question]:
        """
        Retrieves a list of questions, ordered by ID descending.
        """
        stmt = select(Question).offset(skip).limit(limit).order_by(Question.id.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create_answer(db: AsyncSession, question_id: int, schema: AnswerCreate) -> Optional[Answer]:
        """
        Creates an answer for a specific question, if the question exists.
        """
        question = await QAService.get_question(db, question_id)
        if not question:
            return None
        
        db_answer = Answer(question_id=question_id, text=schema.text)
        db.add(db_answer)
        await db.commit()
        await db.refresh(db_answer)
        return db_answer

    @staticmethod
    async def ask_question(db: AsyncSession, schema: AskRequest) -> AskResponse:
        """
        Answers a user question by:
        1. Retrieving top similar documents based on embeddings.
        2. Constructing a prompt context with the retrieved documents.
        3. Querying the OpenAI Chat Completion API with the context.
        4. Storing the question and the generated answer in the database.
        """
        question_text = schema.question.strip()
        if not question_text:
            raise ValueError("Question text cannot be empty or whitespaces only.")
        
        # Verify integration is configured
        if not openai_client and not use_gemini_sdk:
            raise ValueError(
                "API key is not configured. "
                "Please configure OPENAI_API_KEY in your environment or .env file."
            )
        
        # 1. Retrieve similar documents for context (RAG)
        retrieved_contents = []
        try:
            from app.services.document_service import DocumentService
            similar_docs = await DocumentService.search_similar_documents(db, query=question_text, limit=3)
            retrieved_contents = [doc.content for doc, sim in similar_docs]
        except Exception as e:
            # Fallback gracefully if database or retrieval fails
            # (e.g. database not populated yet or tables not fully set up)
            pass

        # 2. Build contextual prompt
        if retrieved_contents:
            context_block = "\n".join([f"- {content}" for content in retrieved_contents])
            system_prompt = (
                "You are a helpful and concise AI Q&A assistant. "
                "You are provided with relevant retrieved document contexts to help answer the user's question. "
                "Please formulate your response using the provided contexts. "
                "If the context does not contain the answer, answer the question to the best of your ability, "
                "but state that the information was not found in the retrieved context."
            )
            user_prompt = f"Context:\n{context_block}\n\nQuestion: {question_text}"
        else:
            system_prompt = "You are a helpful and concise AI Q&A assistant. Answer the user's question clearly."
            user_prompt = question_text

        # Save question to DB
        db_question = Question(text=question_text)
        db.add(db_question)
        await db.commit()
        await db.refresh(db_question)

        # 3. Query LLM endpoint
        try:
            if use_gemini_sdk:
                model_name = settings.OPENAI_MODEL or "gemini-1.5-flash-latest"
                if model_name.startswith("models/"):
                    model_name = model_name[7:]
                
                # Normalize model name for Gemini SDK compatibility
                if "1.5-flash" in model_name:
                    model_name = "gemini-flash-latest"
                elif "1.5-pro" in model_name:
                    model_name = "gemini-pro-latest"
                
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_prompt
                )
                response = await model.generate_content_async(
                    user_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=1000
                    )
                )
                ai_response = response.text.strip()
            else:
                response = await openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                ai_response = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[WARNING] OpenAI Chat Completions failed: {str(e)}. Falling back to mock answer for testing.")
            if retrieved_contents:
                context_summary = "\n".join([f"- {content}" for content in retrieved_contents])
                ai_response = (
                    f"[Mock Answer - OpenAI API error: {str(e)}]\n"
                    f"Question: '{question_text}'\n"
                    f"Context retrieved from Database:\n{context_summary}"
                )
            else:
                ai_response = (
                    f"[Mock Answer - OpenAI API error: {str(e)}]\n"
                    f"Question: '{question_text}'\n"
                    "No relevant contexts were found in the database."
                )

        
        # Save OpenAI answer to DB
        db_answer = Answer(question_id=db_question.id, text=ai_response)
        db.add(db_answer)
        await db.commit()
        
        return AskResponse(
            question=question_text,
            answer=ai_response,
            sources=retrieved_contents
        )



