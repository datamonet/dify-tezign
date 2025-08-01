from flask_login import current_user
from flask_restful import Resource, fields, marshal_with, reqparse

from constants.languages import languages
from controllers.console import api
from controllers.console.wraps import account_initialization_required
from libs.helper import AppIconUrlField
from libs.login import login_required
from services.recommended_app_service import RecommendedAppService

app_fields = {
    "id": fields.String,
    "name": fields.String,
    "mode": fields.String,
    "icon": fields.String,
    "icon_type": fields.String,
    "icon_url": AppIconUrlField,
    "icon_background": fields.String,
}

recommended_app_fields = {
    "app": fields.Nested(app_fields, attribute="app"),
    "app_id": fields.String,
    "description": fields.String(attribute="description"),
    "copyright": fields.String,
    "privacy_policy": fields.String,
    "custom_disclaimer": fields.String,
    "category": fields.String,
    "position": fields.Integer,
    "is_listed": fields.Boolean,
}

recommended_app_list_fields = {
    "recommended_apps": fields.List(fields.Nested(recommended_app_fields)),
    "categories": fields.List(fields.String),
}


class RecommendedAppListApi(Resource):
    @login_required
    @account_initialization_required
    @marshal_with(recommended_app_list_fields)
    def get(self):
        # language args
        parser = reqparse.RequestParser()
        parser.add_argument("language", type=str, location="args")
        args = parser.parse_args()

        if args.get("language") and args.get("language") in languages:
            language_prefix = args.get("language")
        elif current_user and current_user.interface_language:
            language_prefix = current_user.interface_language
        else:
            language_prefix = languages[0]

        return RecommendedAppService.get_recommended_apps_and_categories(language_prefix)

    # code add
    @login_required
    @account_initialization_required
    def post(self):
        """Create Recommended App"""
        parser = reqparse.RequestParser()
        parser.add_argument("app_id", type=str, required=True, location="json")
        parser.add_argument("description", type=str, location="json")
        parser.add_argument("category", type=str, location="json")
        args = parser.parse_args()
        app_detail = RecommendedAppService.get_recommend_app_detail(args["app_id"])
        if app_detail:
            return {"message": "Recommended app already exists"}, 409

        recommended_app_service = RecommendedAppService()
        app = recommended_app_service.create_app(args)

        return app, 201



class RecommendedAppApi(Resource):
    @login_required
    @account_initialization_required
    def get(self, app_id):
        app_id = str(app_id)
        return RecommendedAppService.get_recommend_app_detail(app_id)
    # code add
    @login_required
    @account_initialization_required
    def delete(self, app_id):
        """Delete app"""
        RecommendedAppService().delete_app(app_id)
        return {"result": "success"}, 204

api.add_resource(RecommendedAppListApi, "/explore/apps")
api.add_resource(RecommendedAppApi, "/explore/apps/<uuid:app_id>")
