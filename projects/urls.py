from django.urls import path, include
from .views import ProjectViewSet, ProposalViewSet, retrieveUserProjects,SavedProjectsView,WorkContractView
from django.urls import path, include

from rest_framework import routers

from .views import ProjectViewSet

router = routers.SimpleRouter()
router.register(r"", ProjectViewSet)


urlpatterns = [
    path(
        "proposals/",
        ProposalViewSet.as_view({"get": "list", "post": "create"}),
        name="proposal-list",
    ),
    path(
        "proposals/<int:pk>/",
        ProposalViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="proposal-detail",
    ),
    path(
        "user-projects/",
        retrieveUserProjects,
        name="projects-user",
    ),
    path(
        "saved/",
        SavedProjectsView.as_view(),
        name="saved-projects",
    ),
    path(
        "work-contract/",
        WorkContractView.as_view(),
        name="work-contract",
    ),
]

urlpatterns += router.urls
