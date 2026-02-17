from sqlalchemy import Integer, and_, cast, func, insert, select, text, update
from sqlalchemy.orm import aliased, contains_eager, joinedload, selectinload

from database import (
    Base,
    async_engine,
    async_session_factory,
    session_factory,
    sync_engine,
)
from models import ResumesOrm, VacanciesOrm, WorkersOrm, Workload
from schemas import (
    ResumeRelVacanciesRepliedDTO,
    WorkersDTO,
    WorkersRelDTO,
    WorkloadAvgCompensationDTO,
)


class SyncORM:
    @staticmethod
    def create_tables():
        sync_engine.echo = False
        Base.metadata.drop_all(sync_engine)
        Base.metadata.create_all(sync_engine)
        sync_engine.echo = True

    @staticmethod
    def insert_workers():
        with session_factory() as session:
            worker_bobr = WorkersOrm(username="Bobr")
            worker_volk = WorkersOrm(username="Volk")
            session.add_all([worker_bobr, worker_volk])
            session.commit()


class AsyncORM:
    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            async_engine.echo = False
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            async_engine.echo = True

    @staticmethod
    async def insert_workers():
        async with async_session_factory() as session:
            worker_bobr = WorkersOrm(username="Bobr")
            worker_volk = WorkersOrm(username="Volk")
            session.add_all([worker_bobr, worker_volk])
            await session.flush()
            await session.commit()

    @staticmethod
    async def select_workers():
        async with async_session_factory() as session:
            # worker_id = 1
            # worker_jack = session.get(WorkersOrm, {"id": worker_id})
            # workers = session.get(WorkersOrm, (worker_id, 2, 3))
            # worker_jack = session.get(WorkersOrm, worker_id)
            query = select(WorkersOrm)
            result = await session.execute(query)
            workers = result.scalars().all()
            print(f"{workers=}")

    @staticmethod
    async def update_worker(worker_id: int = 2, new_username: str = "Misha"):
        async with async_session_factory() as session:
            worker_michael = await session.get(WorkersOrm, worker_id)
            worker_michael.username = new_username
            await session.commit()

    @staticmethod
    async def insert_resumes():
        async with async_session_factory() as session:
            resume_jack_1 = ResumesOrm(
                title="Python Junior Developer",
                compensation=50000,
                workload=Workload.fulltime,
                worker_id=1,
            )
            resume_jack_2 = ResumesOrm(
                title="Python Разработчик",
                compensation=150000,
                workload=Workload.fulltime,
                worker_id=1,
            )
            resume_michael_1 = ResumesOrm(
                title="Python Data Engineer",
                compensation=250000,
                workload=Workload.parttime,
                worker_id=2,
            )
            resume_michael_2 = ResumesOrm(
                title="Data Scientist",
                compensation=300000,
                workload=Workload.fulltime,
                worker_id=2,
            )
            session.add_all(
                [resume_jack_1, resume_jack_2, resume_michael_1, resume_michael_2]
            )
            await session.commit()
            sync_engine.echo = True

    @staticmethod
    async def select_resumes_avg_compensation(like_language: str = "Python"):
        """
        select workload, avg(compensation)::int as avg_compensation
        from resumes
        where title like '%Python%' and compensation > 40000
        group by workload
        """
        async with async_session_factory() as session:
            query = (
                select(
                    ResumesOrm.workload,
                    cast(func.avg(ResumesOrm.compensation), Integer).label(
                        "avg_compensation"
                    ),
                )
                .select_from(ResumesOrm)
                .filter(
                    and_(
                        ResumesOrm.title.contains(like_language),
                        ResumesOrm.compensation > 40000,
                    )
                )
                .group_by(ResumesOrm.workload)
                .having(cast(func.avg(ResumesOrm.compensation), Integer) > 70000)
            )
            print(query.compile(compile_kwargs={"literal_binds": True}))
            res = await session.execute(query)
            result = res.all()
            print(result)

    @staticmethod
    async def insert_additional_resumes():
        async with async_session_factory() as session:
            workers = [
                {"username": "Artem"},  # id 3
                {"username": "Roman"},  # id 3
                {"username": "Petr"},  # id 3
            ]
            resumes = [
                {
                    "title": "Python программист",
                    "compensation": 60000,
                    "workload": "fulltime",
                    "worker_id": 3,
                },
                {
                    "title": "Machine learning engineer",
                    "compensation": 70000,
                    "workload": "parttime",
                    "worker_id": 3,
                },
                {
                    "title": "Python data scientist",
                    "compensation": 80000,
                    "workload": "parttime",
                    "worker_id": 4,
                },
                {
                    "title": "Python Analyst",
                    "compensation": 90000,
                    "workload": "fulltime",
                    "worker_id": 4,
                },
                {
                    "title": "Python Junior Developer",
                    "compensation": 100000,
                    "workload": "fulltime",
                    "worker_id": 5,
                },
            ]
            insert_workers = insert(WorkersOrm).values(workers)
            insert_resumes = insert(ResumesOrm).values(resumes)
            await session.execute(insert_workers)
            await session.execute(insert_resumes)
            await session.commit()

    @staticmethod
    async def join_cte_subquery_window_func(like_language: str = "Python"):
        """
        WITH helper2 AS(
            SELECT *, compensation - avg_workload_compensation AS compensation_diff
            FROM
            (SELECT
                w.id,
                w.username,
                r.compensation,
                r.workload,
                avg(r.compensation) OVER (PARTITION BY workload)::int AS avg_workload_compensation
            FROM resumes r
            JOIN workers w on r.worker.id = w.id) helper1
        )
        SELECT * FROM helper2
        ORDER BY compensation_diff DESC;
        """
        async with async_session_factory() as session:
            r = aliased(ResumesOrm)
            w = aliased(WorkersOrm)
            subq = (
                select(
                    r,
                    w,
                    func.avg(r.compensation)
                    .over(partition_by=r.workload)
                    .cast(Integer)
                    .label("avg_workload_compensation"),
                )
                .select_from(r)
                .join(w, r.worker_id == w.id)
                .subquery("helper1")
            )
            cte = select(
                subq.c.id,
                subq.c.username,
                subq.c.compensation,
                subq.c.workload,
                subq.c.avg_workload_compensation,
                (subq.c.compensation - subq.c.avg_workload_compensation).label(
                    "compensation_diff"
                ),
            ).cte("helper2")

            query = select(cte).order_by(cte.c.compensation_diff.desc())
            print(query.compile(compile_kwargs={"literal_binds": True}))

            res = await session.execute(query)
            result = res.all()
            print(f"{result=}")

    @staticmethod
    async def select_workers_with_lazy_relationship():
        async with async_session_factory() as session:
            query = select(WorkersOrm)

            res = await session.execute(query)
            result = res.unique().scalars().all()

            worker_1_resumes = result[0].resumes
            print(worker_1_resumes)

            worker_2_resumes = result[1].resumes
            print(worker_2_resumes)

    @staticmethod
    async def select_workers_with_joined_relationship():
        async with async_session_factory() as session:
            query = select(WorkersOrm).options(joinedload(WorkersOrm.resumes))

            res = await session.execute(query)
            result = res.scalars().all()

            worker_1_resumes = result[0].resumes
            print(worker_1_resumes)

            worker_2_resumes = result[1].resumes
            print(worker_2_resumes)

    @staticmethod
    async def select_workers_with_selectin_relationship():
        async with async_session_factory() as session:
            query = select(WorkersOrm).options(selectinload(WorkersOrm.resumes))

            res = await session.execute(query)
            result = res.scalars().all()

            worker_1_resumes = result[0].resumes
            print(worker_1_resumes)

            worker_2_resumes = result[1].resumes
            print(worker_2_resumes)

    @staticmethod
    async def select_workers_with_condition_relationship():
        async with async_session_factory() as session:
            query = select(WorkersOrm).options(
                selectinload(WorkersOrm.resumes_parttime)
            )

            res = await session.execute(query)
            result = res.scalars().all()

            print(result)

    @staticmethod
    async def select_workers_with_condition_relationship_contains_eager():
        async with async_session_factory() as session:
            query = (
                select(WorkersOrm)
                .join(WorkersOrm.resumes)
                .options(contains_eager(WorkersOrm.resumes))
                .filter(ResumesOrm.workload == "parttime")
            )

            res = await session.execute(query)
            result = res.unique().scalars().all()

            print(result)

    @staticmethod
    async def select_workers_with_condition_relationship_contains_eager_with_limit():
        async with async_session_factory() as session:
            subq = (
                select(ResumesOrm.id.label("parttime_resume_id"))
                .filter(ResumesOrm.worker_id == WorkersOrm.id)
                .order_by(WorkersOrm.id.desc())
                .limit(1)
                .scalar_subquery()
                .correlate(WorkersOrm)
            )

            query = (
                select(WorkersOrm)
                .join(ResumesOrm, ResumesOrm.id.in_(subq))
                .options(contains_eager(WorkersOrm.resumes))
            )

            res = await session.execute(query)
            result = res.unique().scalars().all()

            print(result)

    @staticmethod
    async def select_workers_dto():
        async with async_session_factory() as session:
            query = select(WorkersOrm).limit(2)

            res = await session.execute(query)
            result_orm = res.scalars().all()
            print(f"{result_orm=}")
            result_dto = [
                WorkersDTO.model_validate(row, from_attributes=True)
                for row in result_orm
            ]
            print(f"{result_dto=}")
            return result_dto

    @staticmethod
    async def select_workers_dto_with_relationship():
        async with async_session_factory() as session:
            query = (
                select(WorkersOrm).options(selectinload(WorkersOrm.resumes)).limit(2)
            )

            res = await session.execute(query)
            result_orm = res.scalars().all()
            print(f"{result_orm=}")
            result_dto = [
                WorkersRelDTO.model_validate(row, from_attributes=True)
                for row in result_orm
            ]
            print(f"{result_dto=}")

    @staticmethod
    async def select_workers_dto_group_by():
        async with async_session_factory() as session:
            query = (
                select(
                    ResumesOrm.workload,
                    cast(func.avg(ResumesOrm.compensation), Integer).label(
                        "avg_compensation"
                    ),
                )
                .select_from(ResumesOrm)
                .filter(
                    and_(
                        ResumesOrm.title.contains("Python"),
                        ResumesOrm.compensation > 40000,
                    )
                )
                .group_by(ResumesOrm.workload)
                .having(cast(func.avg(ResumesOrm.compensation), Integer) > 70000)
            )
            print(query.compile(compile_kwargs={"literal_binds": True}))
            res = await session.execute(query)
            result_orm = res.all()
            print(f"{result_orm=}")
            result_dto = [
                WorkloadAvgCompensationDTO.model_validate(row, from_attributes=True)
                for row in result_orm
            ]
            print(f"{result_dto=}")

    @staticmethod
    async def add_vacancies_and_replies():
        async with async_session_factory() as session:
            new_vacancy = VacanciesOrm(title="Python Разработчик", compensation=100000)
            resume_1 = await session.get(
                ResumesOrm, 1, options=[selectinload(ResumesOrm.vacancies_replied)]
            )
            resume_2 = await session.get(
                ResumesOrm, 2, options=[selectinload(ResumesOrm.vacancies_replied)]
            )
            if resume_1:
                resume_1.vacancies_replied.append(new_vacancy)
            if resume_2:
                resume_2.vacancies_replied.append(new_vacancy)
            await session.commit()

    @staticmethod
    async def select_resumes_with_all_relationship():
        async with async_session_factory() as session:
            query = (
                select(ResumesOrm)
                .options(joinedload(ResumesOrm.worker))
                .options(selectinload(ResumesOrm.vacancies_replied))
            )

            res = await session.execute(query)
            result_orm = res.unique().scalars().all()
            print(f"{result_orm=}")
            result_dto = [
                ResumeRelVacanciesRepliedDTO.model_validate(row, from_attributes=True)
                for row in result_orm
            ]
            print(f"{result_dto=}")
