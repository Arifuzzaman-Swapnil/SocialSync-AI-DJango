"""
V1.2.1 RBAC Management Views
- List workspace roles
- Assign / remove roles
- Get current user's roles
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User

from accounts.models import UserRole
from brands.models import Workspace
from .serializers import UserRoleSerializer, AssignRoleSerializer, RemoveRoleSerializer


class WorkspaceRolesView(APIView):
    """List all role assignments for a workspace"""
    permission_classes = [IsAuthenticated]

    def get(self, request, workspace_id):
        try:
            workspace = Workspace.objects.get(id=workspace_id)
        except Workspace.DoesNotExist:
            return Response({'error': 'Workspace not found'}, status=status.HTTP_404_NOT_FOUND)

        # Only owner/admin can view roles
        if workspace.owner != request.user and not UserRole.has_role(request.user, workspace, 'admin'):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        roles = UserRole.objects.filter(workspace=workspace).select_related('user', 'granted_by')
        serializer = UserRoleSerializer(roles, many=True)

        # Also include the owner
        return Response({
            'owner': {
                'user_id': workspace.owner.id,
                'username': workspace.owner.username,
                'role': 'owner',
            },
            'roles': serializer.data,
        })


class AssignRoleView(APIView):
    """Assign a role to a user in a workspace"""
    permission_classes = [IsAuthenticated]

    def post(self, request, workspace_id):
        try:
            workspace = Workspace.objects.get(id=workspace_id)
        except Workspace.DoesNotExist:
            return Response({'error': 'Workspace not found'}, status=status.HTTP_404_NOT_FOUND)

        # Only owner/admin can assign roles
        if workspace.owner != request.user and not UserRole.has_role(request.user, workspace, 'admin'):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = AssignRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            target_user = User.objects.get(id=data['user_id'])
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        role, created = UserRole.objects.get_or_create(
            user=target_user,
            workspace=workspace,
            role=data['role'],
            defaults={'granted_by': request.user},
        )

        if not created:
            return Response({'message': 'Role already assigned'}, status=status.HTTP_200_OK)

        return Response(
            UserRoleSerializer(role).data,
            status=status.HTTP_201_CREATED,
        )


class RemoveRoleView(APIView):
    """Remove a role from a user in a workspace"""
    permission_classes = [IsAuthenticated]

    def post(self, request, workspace_id):
        try:
            workspace = Workspace.objects.get(id=workspace_id)
        except Workspace.DoesNotExist:
            return Response({'error': 'Workspace not found'}, status=status.HTTP_404_NOT_FOUND)

        # Only owner/admin can remove roles
        if workspace.owner != request.user and not UserRole.has_role(request.user, workspace, 'admin'):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = RemoveRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        deleted, _ = UserRole.objects.filter(
            user_id=data['user_id'],
            workspace=workspace,
            role=data['role'],
        ).delete()

        if deleted == 0:
            return Response({'error': 'Role not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'Role removed'})


class MyRolesView(APIView):
    """Get current user's roles across all workspaces"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        roles = UserRole.objects.filter(user=request.user).select_related('workspace')

        # Include owned workspaces
        owned = Workspace.objects.filter(owner=request.user).values_list('id', 'name')
        owned_list = [{'workspace_id': wid, 'workspace_name': wname, 'role': 'owner'} for wid, wname in owned]

        assigned_list = [
            {
                'workspace_id': r.workspace_id,
                'workspace_name': r.workspace.name,
                'role': r.role,
            }
            for r in roles
        ]

        return Response({
            'roles': owned_list + assigned_list,
        })
