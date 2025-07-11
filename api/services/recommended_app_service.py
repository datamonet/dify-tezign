import os
from typing import Optional

import requests
from flask_sqlalchemy.pagination import Pagination

from configs import dify_config
from models.model import Account, App, RecommendedApp, db
from services.recommend_app.recommend_app_factory import RecommendAppRetrievalFactory



class RecommendedAppService:
    @classmethod
    def get_recommended_apps_and_categories(cls, language: str) -> dict:
        """
        Get recommended apps and categories.
        :param language: language
        :return:
        """
        mode = dify_config.HOSTED_FETCH_APP_TEMPLATES_MODE
        retrieval_instance = RecommendAppRetrievalFactory.get_recommend_app_factory(mode)()
        result = retrieval_instance.get_recommended_apps_and_categories(language)
        if not result.get("recommended_apps") and language != "en-US":
            result = (
                RecommendAppRetrievalFactory.get_buildin_recommend_app_retrieval().fetch_recommended_apps_from_builtin(
                    "en-US"
                )
            )

        return result

    @classmethod
    def get_recommend_app_detail(cls, app_id: str) -> Optional[dict]:
        """
        Get recommend app detail.
        :param app_id: app id
        :return:
        """
        mode = dify_config.HOSTED_FETCH_APP_TEMPLATES_MODE
        retrieval_instance = RecommendAppRetrievalFactory.get_recommend_app_factory(mode)()
        result: dict = retrieval_instance.get_recommend_app_detail(app_id)
        return result

    # code add:publish api,创建推荐应用
    def create_app(self, args: dict) -> dict:
        # 检查App是否存在
        app_to_update = db.session.query(App).filter_by(id=args["app_id"]).first()
        if not app_to_update:
            raise ValueError(f"App with id {args['app_id']} does not exist")

        # 检查是否已存在
        existing_app = db.session.query(RecommendedApp).filter_by(app_id=args["app_id"]).first()
        if existing_app:
            # 如果已存在，更新updated_at
            existing_app.updated_at = datetime.datetime.utcnow()
            db.session.commit()
            return {"id": existing_app.id}

        # 如果不存在，创建新的推荐
        app = RecommendedApp(
            app_id=args["app_id"],
            category=args.get("category", ""),
            description=args.get("description", ""),
            copyright="",
            privacy_policy="",
        )

        # 将app添加到session并提交
        db.session.add(app)
        
        # 更新app的公开状态
        app_to_update.is_public = True
        db.session.commit()

        return {"id": app.id}


    # takin code:publish api,删除推荐应用
    def delete_app(self, id: str) -> None:
        """
        Delete recommended app
        """
        try:
            app_to_delete = db.session.query(RecommendedApp).filter_by(app_id=id).one()

            db.session.delete(app_to_delete)
            db.session.commit()
        except Exception as e:
            # logging.exception(f"An error occurred: {e}")
            db.session.rollback()