# apps/community/reports/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.core.exceptions import ValidationError as DjangoValidationError

from .serializers import ReportRequestIn, ReportCreatedOut
from .services import create_post_report
from .repositories import DuplicateReportError, TargetNotFoundError


class PostReportView(APIView):
    """
    POST /posts/{post_id}/report
    - 로그인 필수
    - 포스트만 신고 가능
    - reason: 한글 라벨 (스펙 열거)
    - detail: '기타'일 때 5자 이상
    - 중복 신고(동일 user+post) 시 409
    """
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
                public_post_id=post_id,  # 공개(base64) ID 그대로 전달
                reason_label=in_ser.validated_data["reason"],
                detail=in_ser.validated_data.get("detail") or "",
            )
        except ValueError as _e:  # 잘못된 base64 ID
            return Response({"code": "BAD_ID", "message": str(_e)}, status=status.HTTP_400_BAD_REQUEST)
        except DjangoValidationError as _e:  # '기타' 5자 미만 등
            msg = getattr(_e, "message", None) or getattr(_e, "messages", [None])[0] or str(_e)
            return Response({"code": "VALIDATION_ERROR", "message": msg}, status=status.HTTP_400_BAD_REQUEST)
        except TargetNotFoundError:
            return Response({"code": "NOT_FOUND", "message": "리소스를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except DuplicateReportError:
            return Response({"code": "CONFLICT", "message": "이미 처리된 요청입니다."}, status=status.HTTP_409_CONFLICT)

        out_ser = ReportCreatedOut({"report_id": report.id})
        return Response(out_ser.data, status=status.HTTP_201_CREATED)
