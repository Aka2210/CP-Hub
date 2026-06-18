import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.group_task import GroupTask
from backend.app.models.group_task_problem import GroupTaskProblem
from backend.app.models.user import User

_PROBLEM_EAGER_LOAD = (
    selectinload(GroupTask.problems).selectinload(GroupTaskProblem.claimed_by_user),
    # completed_by_user.stats is loaded too since finalize() awards bonus rewards directly onto it.
    selectinload(GroupTask.problems).selectinload(GroupTaskProblem.completed_by_user).selectinload(User.stats),
)


async def get_active_task(session: AsyncSession) -> GroupTask | None:
    result = await session.execute(select(GroupTask).where(GroupTask.status == "active").options(*_PROBLEM_EAGER_LOAD))
    return result.scalar_one_or_none()


async def get_task_with_problems(session: AsyncSession, task_id: uuid.UUID) -> GroupTask | None:
    result = await session.execute(select(GroupTask).where(GroupTask.id == task_id).options(*_PROBLEM_EAGER_LOAD))
    return result.scalar_one_or_none()


async def create_task(
    session: AsyncSession,
    *,
    deadline: datetime,
    reward_exp: int,
    reward_coins: int,
    created_by: int,
    channel_id: int,
    problems: list[dict],
) -> GroupTask:
    """`problems` entries must already contain code/difficulty/title/url/title_slug."""
    task = GroupTask(
        deadline=deadline,
        reward_exp=reward_exp,
        reward_coins=reward_coins,
        created_by=created_by,
        channel_id=channel_id,
        problems=[
            GroupTaskProblem(
                code=p["code"],
                difficulty=p["difficulty"],
                title=p["title"],
                url=p["url"],
                title_slug=p["title_slug"],
            )
            for p in problems
        ],
    )
    session.add(task)
    await session.commit()
    return await get_task_with_problems(session, task.id)


async def delete_task(session: AsyncSession, task_id: uuid.UUID) -> None:
    task = await session.get(GroupTask, task_id)
    if task is not None:
        await session.delete(task)
        await session.commit()


async def get_problems_by_codes(session: AsyncSession, task_id: uuid.UUID, codes: list[str]) -> list[GroupTaskProblem]:
    result = await session.execute(
        select(GroupTaskProblem)
        .where(GroupTaskProblem.group_task_id == task_id, GroupTaskProblem.code.in_(codes))
        .options(selectinload(GroupTaskProblem.claimed_by_user), selectinload(GroupTaskProblem.completed_by_user))
    )
    return list(result.scalars().all())


async def get_claimed_incomplete_by_user(session: AsyncSession, task_id: uuid.UUID, user_id: uuid.UUID) -> list[GroupTaskProblem]:
    result = await session.execute(
        select(GroupTaskProblem).where(
            GroupTaskProblem.group_task_id == task_id,
            GroupTaskProblem.claimed_by == user_id,
            GroupTaskProblem.is_completed.is_(False),
        )
    )
    return list(result.scalars().all())


async def mark_claimed(session: AsyncSession, problem: GroupTaskProblem, user_id: uuid.UUID) -> None:
    problem.claimed_by = user_id
    problem.claimed_at = datetime.now(timezone.utc)
    await session.commit()


async def mark_unclaimed(session: AsyncSession, problem: GroupTaskProblem) -> None:
    problem.claimed_by = None
    problem.claimed_at = None
    await session.commit()


async def mark_completed(session: AsyncSession, problem: GroupTaskProblem, user_id: uuid.UUID) -> None:
    problem.is_completed = True
    problem.completed_by = user_id
    problem.completed_at = datetime.now(timezone.utc)
    await session.commit()


async def finalize_task(session: AsyncSession, task_id: uuid.UUID, status: str) -> GroupTask | None:
    """Atomically transitions the task out of 'active'. Returns None if it was already finalized by another path."""
    result = await session.execute(
        update(GroupTask).where(GroupTask.id == task_id, GroupTask.status == "active").values(status=status, completed_at=datetime.now(timezone.utc))
    )
    await session.commit()

    if result.rowcount == 0:
        return None

    return await get_task_with_problems(session, task_id)
