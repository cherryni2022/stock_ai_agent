"""User, ChatSession, and ChatMessage repositories."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from stock_agent.database.models.agent_log import AgentExecutionLog
from stock_agent.database.models.user import ChatMessage, ChatSession, User
from stock_agent.database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """用户 Repository."""

    model = User

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_or_create(self, username: str, email: str | None = None) -> User:
        """Get existing user or create a new one."""
        user = await self.get_by_username(username)
        if user is None:
            user = User(username=username, email=email)
            self.session.add(user)
            await self.session.flush()
            await self.session.refresh(user)
        return user


class ChatSessionRepository(BaseRepository[ChatSession]):
    """聊天会话 Repository."""

    model = ChatSession

    async def get_with_messages(self, session_id: str) -> ChatSession | None:
        """获取会话及其所有消息."""
        stmt = (
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(ChatSession.id == session_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_user_sessions(self, user_id: str, limit: int = 50) -> list[ChatSession]:
        """获取用户的所有会话 (最新在前)."""
        stmt = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_session(self, user_id: str, title: str = "新对话") -> ChatSession:
        """创建新会话."""
        session = ChatSession(user_id=user_id, title=title)
        self.session.add(session)
        await self.session.flush()
        await self.session.refresh(session)
        return session


class ChatMessageRepository(BaseRepository[ChatMessage]):
    """聊天消息 Repository."""

    model = ChatMessage

    async def get_session_messages(
        self,
        session_id: str,
        limit: int = 100,
    ) -> list[ChatMessage]:
        """获取会话中的消息 (按时间正序)."""
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_message(self, session_id: str, role: str, content: str) -> ChatMessage:
        """添加一条消息."""
        msg = ChatMessage(session_id=session_id, role=role, content=content)
        self.session.add(msg)
        await self.session.flush()
        await self.session.refresh(msg)
        return msg


class AgentLogRepository(BaseRepository[AgentExecutionLog]):
    """Agent 执行日志 Repository."""

    model = AgentExecutionLog

    async def get_session_logs(
        self,
        session_id: str,
        limit: int = 50,
    ) -> list[AgentExecutionLog]:
        """获取某会话的所有执行日志."""
        stmt = (
            select(AgentExecutionLog)
            .where(AgentExecutionLog.session_id == session_id)
            .order_by(AgentExecutionLog.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_logs(self, limit: int = 20) -> list[AgentExecutionLog]:
        """获取最近的执行日志."""
        stmt = (
            select(AgentExecutionLog)
            .order_by(AgentExecutionLog.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
