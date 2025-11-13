from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.core.exceptions import ValidationError as DjangoValidationError

from .serializers import ReportRequestIn, ReportCreatedOut
from .services import create_post_report
from .repositories import DuplicateReportError, TargetNotFoundError


class PostReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id: str):
        in_ser = ReportRequestIn(data=request.data)
        if not in_ser.is_valid():
            return Response(
                {"code": "VALIDATION_ERROR", "message": "요청 형식이 올바르지 않습니다.", "field_errors": in_ser.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            report = create_post_report(
                user=request.user,
                public_post_id=post_id,
                reason_label=in_ser.validated_data["reason"],
                detail=in_ser.validated_data.get("detail") or "",
            )
        except ValueError as _e:
            return Response({"code": "BAD_ID", "message": str(_e)}, status=status.HTTP_400_BAD_REQUEST)
        except DjangoValidationError as _e:
            msg = getattr(_e, "message", None) or getattr(_e, "messages", [None])[0] or str(_e)
            return Response({"code": "VALIDATION_ERROR", "message": msg}, status=status.HTTP_400_BAD_REQUEST)
        except TargetNotFoundError:
            return Response({"code": "NOT_FOUND", "message": "리소스를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except DuplicateReportError:
            return Response({"code": "CONFLICT", "message": "이미 처리된 요청입니다."}, status=status.HTTP_409_CONFLICT)

        out_ser = ReportCreatedOut({"report_id": report.id})
        return Response(out_ser.data, status=status.HTTP_201_CREATED)
