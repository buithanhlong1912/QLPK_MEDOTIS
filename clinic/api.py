
from finance.models import (
    HoaDonChuoiKham, 
    HoaDonThuoc, 
    HoaDonLamSang
)
from finance.serializers import HoaDonChuoiKhamSerializer
from json import dump
from rest_framework.parsers import FileUploadParser
from rest_framework.parsers import MultiPartParser
import json
from medicine.models import DonThuoc, Thuoc, TrangThaiDonThuoc, VatTu
from django.http.response import Http404, HttpResponse, JsonResponse
from rest_framework import views
from rest_framework.views import APIView
from clinic.models import (
    BaiDang, 
    DichVuKham, 
    FileKetQua, 
    KetQuaTongQuat, 
    LichHenKham, 
    PhanKhoaKham, 
    PhongChucNang, 
    PhongKham, 
    TrangThaiChuoiKham, 
    TrangThaiKhoaKham, 
    TrangThaiLichHen, 
    ChuoiKham, 
    KetQuaChuyenKhoa, 
    BacSi
)
from rest_framework import viewsets
from django.contrib.auth import authenticate, get_user_model
from .serializers import (BaiDangSerializer, BookLichHenKhamSerializer,DangKiSerializer, DanhSachDonThuocSerializer, DanhSachPhanKhoaSerializer, DanhSachPhongKhamSerializer,DichVuKhamSerializer, DonThuocSerializer, FileKetQuaSerializer,HoaDonChuoiKhamSerializerSimple, HoaDonThuocSerializer,HoaDonThuocSerializerSimple, KetQuaTongQuatSerializer,LichHenKhamSerializer, LichHenKhamSerializerSimple, LichHenKhamUserSerializer,PhanKhoaKhamDichVuSerializer, PhanKhoaKhamSerializer,PhongChucNangSerializer, PhongChucNangSerializerSimple,ProfilePhongChucNangSerializer, TrangThaiLichHenSerializer,UserLoginSerializer, UserSerializer, ChuoiKhamSerializer,UserUpdateInfoSerializer, UserUpdateInfoRequestSerializer,UploadAvatarSerializer, AppointmentUpdateDetailSerializer,UpdateLichHenKhamSerializer, DichVuKhamHoaDonSerializer,HoaDonChuoiKhamThanhToanSerializer, KetQuaChuyenKhoaSerializer,  ChuoiKhamSerializerSimple, UserSerializerSimple, VatTuSerializer,DanhSachDichVuSerializer, HoaDonLamSangSerializer, DanhSachBacSiSerializer)
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncDay
from django.db.models import Count, F, Sum, Q
from django.db import models
from medicine.serializers import (
    DanhSachThuocSerializer, 
    KeDonThuocSerializer,
    ThuocSerializer
)
from rest_framework import pagination
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def list(self, request):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True, context={"request": request})

        user_data = serializer.data

        ds_user_moi = []

        for user in user_data:
            child_user = User.objects.filter(parent = user['id'])
            child_user_serializer = UserSerializer(child_user, many=True)
            user['child'] = child_user_serializer.data
            ds_user_moi.append(user)

        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh sach Nguoi dung",
            "data": ds_user_moi,
        }
        return Response(response)

    def create(self, request):
        try:
            user_serializer = UserSerializer(data=request.data, context={"request": request})
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        
            response = {
                "error": False,
                "status": status.HTTP_201_CREATED,
                "message" : "Them Nguoi Dung Thanh Cong",
            }
        except:
            response = {
                "error": True,
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Moi Nguoi Dung",
            }

        return Response(response)

    # def retrieve(self, request: Request, pk=None):
    #     queryset = User.objects.all()
    #     user = get_object_or_404(queryset, pk=pk)
    #     serializer = UserSerializer(user, context={"request": request})

    #     user_data = serializer.data

    #     return Response({"error":False, "status": status.HTTP_200_OK, "message":"Single Data Fetch", "data":user_data})
    
    def retrieve(self, request: Request, *args, **kwargs):
        if kwargs.get('pk') == 'me':
            return Response(self.get_serializer(request.user).data)
        else:
            queryset = User.objects.all()
            user = get_object_or_404(queryset, pk=kwargs.get('pk'))
            serializer = UserSerializer(user, context={"request": request})
            user_data = serializer.data
            return Response({"error":False, "status": status.HTTP_200_OK, "message":"Single Data Fetch", "data":user_data})
        return super().retrieve(request, **kwargs)

    # TODO set quyền cho người dùng, chỉ có admin mới thấy được chi tiết của từng người dùng, còn lại mỗi người dùng chỉ thấy được chi tiết của họ

    def update(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        
        serialzer = UserSerializer(user, data=request.data, context={"request": request})
        serialzer.is_valid()
        serialzer.save()

        # for child_user_data in request.data["parent"]:
        #     print(child_user_data)

        # try:
        #     for child_user_data in request.data["parent"]:
        #         if child_user_data["id"] == 0:
        #             # tao moi 1 tai khoan con

        #             del child_user_data["id"]
        #             child_user_data["parent"] = serialzer.data["id"]
        #             child_user_serializer = UserSerializer(data=child_user_data, context={"request": request})
        #             child_user_serializer.is_valid()
        #             child_user_serializer.save()
        #         else:
        #             # update tai khoan con
        #             queryset2 = User.objects.all()
        #             child_user = get_object_or_404(queryset2, pk=child_user_data["id"])
        #             del child_user_data["id"]
        #             child_user_serializer = UserSerializer(child_user, data=child_user_data, context={"request": request})
        #             child_user_serializer.is_valid()
        #             child_user_serializer.save()
            
        #     return Response({"error": True, "message": child_user_serializer.error_messages})
        # except:
        # return Response({"error": True, "message": serialzer.error_messages})
        return Response({"error": False, "status": status.HTTP_200_OK, "message": "Cap Nhat Du Lieu Thanh Cong"})

    # TODO create JWT authentication

class DangNhapAPI(views.APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request,
                so_dien_thoai = serializer.validated_data['so_dien_thoai'],
                password = serializer.validated_data['password']
            )
            try:
                u = User.objects.get(so_dien_thoai=serializer.validated_data['so_dien_thoai'])
            except:
                return Response({
                    "error_message": "Số Điện Thoại Hoặc Mật Khẩu Không Đúng",
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
        
            user_serializer = UserSerializerSimple(u, context={'request': request})
            if user:
                refresh = TokenObtainPairSerializer.get_token(user)
                data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'access_expires': int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()),
                    'refresh_expires': int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()),
                    'user_id': u.id,
                    'user_data': user_serializer.data
                }
                return Response(data, status=status.HTTP_200_OK)
            return Response({
                "error_message": "Số Điện Thoại Hoặc Mật Khẩu Không Đúng",
                'error_code': 400,
            },status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "error_message": serializer.errors,
            "error_code": 400
        }, status=status.HTTP_400_BAD_REQUEST)

class DangKiAPI(generics.GenericAPIView):
    serializer_class = DangKiSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "status": status.HTTP_201_CREATED,
            "message": "Đăng Kí Tài Khoản Thành Công"
        })

class DichVuKhamViewSet(viewsets.ViewSet):

    def list(self, request):
        phong_chuc_nang = PhongChucNangSerializerSimple()
        dich_vu_kham = DichVuKham.objects.all()
        serializer = DichVuKhamSerializer(dich_vu_kham, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Dich Vu Kham",
            "data": serializer.data
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = DichVuKhamSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": "Them Dich Vu Kham Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Dich Vu Kham"
            }
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = DichVuKham.objects.all()
        dich_vu_kham = get_object_or_404(queryset, pk=pk)
        serializer = DichVuKhamSerializer(dich_vu_kham, context={"request": request})
        data = serializer.data
        response = {
            "error": False, 
            "status": status.HTTP_200_OK,
            "message": f"Dich Vu: {dich_vu_kham.ten_dich_vu}",
            "data": data
        }
        return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = DichVuKham.objects.all()
            dich_vu_kham = get_object_or_404(queryset, pk=pk)
            serializer = DichVuKhamSerializer(dich_vu_kham, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": f"Cap Nhat Dich Vu {dich_vu_kham.ten_dich_vu} Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Dich Vu",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = DichVuKham.objects.all()
        dich_vu_kham = get_object_or_404(queryset, pk=pk)
        dich_vu_kham.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": f"Xoa Dich Vu {dich_vu_kham.ten_dich_vu} Thanh Cong"
        })

class PhongChucNangViewSet(viewsets.ModelViewSet):
    def list(self, request):
        phong_chuc_nang = PhongChucNang.objects.all()
        serializer = PhongChucNangSerializer(phong_chuc_nang, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Phong Chuc Nang",
            "data": serializer.data
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = PhongChucNangSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": "Them Phong Chuc Nang Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Phong Chuc Nang"
            }
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = PhongChucNang.objects.all()
        phong_chuc_nang = get_object_or_404(queryset, pk=pk)
        serializer = PhongChucNangSerializer(phong_chuc_nang, context={"request": request})
        data = serializer.data
        response = {
            "error": False, 
            "status": status.HTTP_200_OK,
            "message": f"Phong Chuc Nang: {phong_chuc_nang.ten_phong_chuc_nang}",
            "data": data
        }
        return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = PhongChucNang.objects.all()
            phong_chuc_nang = get_object_or_404(queryset, pk=pk)
            serializer = PhongChucNangSerializer(phong_chuc_nang, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": f"Cap Nhat Phong Chuc Nang {phong_chuc_nang.ten_phong_chuc_nang} Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Phong Chuc Nang",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = PhongChucNang.objects.all()
        phong_chuc_nang = get_object_or_404(queryset, pk=pk)
        phong_chuc_nang.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": f"Xóa Phòng Chức Năng {phong_chuc_nang.ten_phong_chuc_nang} Thành Công"
        })

class LichHenKhamViewSet(viewsets.ModelViewSet):
    serializer_class = LichHenKhamSerializer

    def list(self, request):
        # trang_thai = TrangThaiLichHen.objects.filter(Q(ten_trang_thai="Thanh Toán Lâm Sàng") | Q(ten_trang_thai = "Chờ Thanh Toán"))
        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Đã Thanh Toán Lâm Sàng")[0] 
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)

        lich_hen = LichHenKham.objects.filter(trang_thai=trang_thai, thoi_gian_bat_dau__lte=today_end)
        # lich_hen = LichHenKham.objects.filter(trang_thai = trang_thai).annotate(relevance=models.Case(
        #     models.When(thoi_gian_bat_dau__gte=now, then=1),
        #     models.When(thoi_gian_bat_dau__lt=now, then=2),
        #     output_field=models.IntegerField(),
        # )).annotate(
        # timediff=models.Case(
        #     models.When(thoi_gian_bat_dau__gte=now, then= F('thoi_gian_bat_dau') - now),
        #     models.When(thoi_gian_bat_dau__lt=now, then=now - F('thoi_gian_bat_dau')),
        #     # models.When(thoi_gian_bat_dau__lte=today_end - F('thoi_gian_bat_dau')),
        #     output_field=models.DurationField(),
        # )).order_by('relevance', 'timediff')
        # upcoming_events = []
        # for lich in lich_hen:
        #     if lich.relevance == 1:
        #         upcoming_events.append(lich)

        serializer = LichHenKhamSerializer(lich_hen, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Lich Hen Kham",
            "data": serializer.data        
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = LichHenKhamSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": "Them Lich Hen Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Lich Hen"
            }
        return Response(response)

    def retrieve(self, request: Request, *args, **kwargs):
        if kwargs.get('pk') == 'me':
            queryset = LichHenKham.objects.filter(benh_nhan=request.user)
            serializer = LichHenKhamSerializer(queryset, many=True, context={"request": request})
            return Response(serializer.data)
        else:
            queryset = LichHenKham.objects.all()
            lich_hen = get_object_or_404(queryset, pk=kwargs.get('pk'))
            serializer = LichHenKhamSerializer(lich_hen, context={"request": request})
            data = serializer.data
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Lich Hen",
                "data": data
            }
            return Response(response)
        return super().retrieve(*args, **kwargs)

    def update(self, request, pk=None):
        try:
            queryset = LichHenKham.objects.all()
            lich_hen = get_object_or_404(queryset, pk=pk)
            serializer = LichHenKhamSerializer(lich_hen, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Cap Nhat Lich Hen Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Lich Hen",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = LichHenKham.objects.all()
        lich_hen = get_object_or_404(queryset, pk=pk)
        lich_hen.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Xoa Lich Hen Thanh Cong"
        })

    # NOTE: khi lễ tân cập nhật lịch hẹn, sẽ tự động cập nhật trường nguoi_phu_trach
    # def perform_update(self, serializer):
    #     serializer.save(nguoi_phu_trach=self.request.user)

class TrangThaiLichHenViewSet(viewsets.ModelViewSet):
    def list(self, request):
        trang_thai_lich_hen = TrangThaiLichHen.objects.all()
        serializer = TrangThaiLichHenSerializer(trang_thai_lich_hen, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Trang Thai Lich Hen",
            "data": serializer.data        
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = TrangThaiLichHenSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": f"Them Trang Thai Lich Hen Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Trang Thai Lich Hen"
            }
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = TrangThaiLichHen.objects.all()
        trang_thai_lich_hen = get_object_or_404(queryset, pk=pk)
        serializer = TrangThaiLichHenSerializer(trang_thai_lich_hen, context={"request": request})
        data = serializer.data
        response = {
            "error": False, 
            "status": status.HTTP_200_OK,
            "message": "Lich Hen",
            "data": data
        }
        return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = TrangThaiLichHen.objects.all()
            trang_thai_lich_hen = get_object_or_404(queryset, pk=pk)
            serializer = TrangThaiLichHenSerializer(trang_thai_lich_hen, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Cap Nhat Lich Hen Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Lich Hen",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = TrangThaiLichHen.objects.all()
        trang_thai_lich_hen = get_object_or_404(queryset, pk=pk)
        trang_thai_lich_hen.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Xoa Lich Hen Thanh Cong"
        })

class ChuoiKhamViewSet(viewsets.ModelViewSet):
    queryset = ChuoiKham.objects.all()
    serializer_class = ChuoiKhamSerializer

    def get_queryset(self):
        if self.action == 'retrieve': 
            return self.queryset.filter(benh_nhan=self.request.user)
        return self.queryset

    def list(self, request):
        chuoi_kham = ChuoiKham.objects.select_related('benh_nhan').all().order_by("-thoi_gian_tao")
        serializer = ChuoiKhamSerializer(chuoi_kham, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Chuoi Kham",
            "data": serializer.data        
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = ChuoiKhamSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": f"Them Chuoi Kham Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Chuoi Kham"
            }
        return Response(response)

    def retrieve(self, request, *args, **kwargs):
        if kwargs.get('pk') == 'me':
            chuoi_kham = ChuoiKham.objects.filter(benh_nhan=request.user.id)
            serializer = ChuoiKhamSerializer(chuoi_kham, many=True, context={"request": request})
            return Response(serializer.data)
        else:
            queryset = ChuoiKham.objects.all()
            chuoi_kham = get_object_or_404(queryset, pk=kwargs.get('pk'))

            serializer = ChuoiKhamSerializer(chuoi_kham, context={"request": request})
            data = serializer.data
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Chuoi Kham",
                "data": data
            }
            return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = ChuoiKham.objects.all()
            chuoi_kham = get_object_or_404(queryset, pk=pk)
            serializer = ChuoiKhamSerializer(chuoi_kham, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Cap Nhat Chuoi Kham Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Chuoi Kham"
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = ChuoiKham.objects.all()
        chuoi_kham = get_object_or_404(queryset, pk=pk)
        chuoi_kham.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Xoa Chuoi Kham Thanh Cong"
        })

    # TODO chuỗi khám sẽ query theo user, từng user sẽ có 1 list các chuỗi khám
    
    # TODO điều phối khám cho bệnh nhân 

class KetQuaTongQuatViewSet(viewsets.ModelViewSet):
    def list(self, request):
        ket_qua_tong_quat = KetQuaTongQuat.objects.all()
        serializer = KetQuaTongQuatSerializer(ket_qua_tong_quat, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Ket Qua Tong Quat",
            "data": serializer.data        
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = KetQuaTongQuatSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": f"Them Ket Qua Tong Quat Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Ket Qua Tong Quat"
            }
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = KetQuaTongQuat.objects.all()
        ket_qua_tong_quat = get_object_or_404(queryset, pk=pk)
        serializer = KetQuaTongQuatSerializer(ket_qua_tong_quat, context={"request": request})
        data = serializer.data
        response = {
            "error": False, 
            "status": status.HTTP_200_OK,
            "message": "Ket Qua Tong Quat",
            "data": data
        }
        return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = KetQuaTongQuat.objects.all()
            ket_qua_tong_quat = get_object_or_404(queryset, pk=pk)
            serializer = KetQuaTongQuatSerializer(ket_qua_tong_quat, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Cap Nhat Ket Qua Tong Quat Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Ket Qua Tong Quat",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = KetQuaTongQuat.objects.all()
        ket_qua_tong_quat = get_object_or_404(queryset, pk=pk)
        ket_qua_tong_quat.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Xoa Ket Qua Tong Quat Thanh Cong"
        })
    
    # TODO kết quả tổng quát sẽ query theo chuỗi khám, mỗi chuỗi khám sẽ có một kết quả tổng quát

class KetQuaChuyenKhoaViewSet(viewsets.ModelViewSet):
    def list(self, request):
        ket_qua_chuyen_khoa = KetQuaChuyenKhoa.objects.all()
        serializer = KetQuaChuyenKhoaSerializer(ket_qua_chuyen_khoa, many=True, context={"request": request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Ket Qua Chuyen Khoa",
            "data": serializer.data        
        }
        return Response(response)

    def create(self, request):
        try:
            serializer = KetQuaChuyenKhoaSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_201_CREATED,
                "message": f"Them Ket Qua Chuyen Khoa Thanh Cong"
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Them Ket Qua Chuyen Khoa"
            }
        return Response(response)

    def retrieve(self, request, pk=None):
        queryset = KetQuaChuyenKhoa.objects.all()
        ket_qua_chuyen_khoa = get_object_or_404(queryset, pk=pk)
        serializer = KetQuaChuyenKhoaSerializer(ket_qua_chuyen_khoa, context={"request": request})
        data = serializer.data
        response = {
            "error": False, 
            "status": status.HTTP_200_OK,
            "message": "Ket Qua Chuyen Khoa",
            "data": data
        }
        return Response(response)   

    def update(self, request, pk=None):
        try:
            queryset = KetQuaChuyenKhoa.objects.all()
            ket_qua_chuyen_khoa = get_object_or_404(queryset, pk=pk)
            serializer = KetQuaChuyenKhoaSerializer(ket_qua_chuyen_khoa, data=request.data, context={"request": request})
            serializer.is_valid()
            serializer.save()
            response = {
                "error": False, 
                "status": status.HTTP_200_OK,
                "message": "Cap Nhat Ket Qua Chuyen Khoa Thanh Cong",
                "data": serializer.data
            }
        except:
            response = {
                "error": True, 
                "status": status.HTTP_409_CONFLICT,
                "message": "Khong The Cap Nhat Ket Qua Chuyen Khoa",
            }
        return Response(response)

    def destroy(self, request, pk=None):
        queryset = KetQuaChuyenKhoa.objects.all()
        ket_qua_chuyen_khoa = get_object_or_404(queryset, pk=pk)
        ket_qua_chuyen_khoa.delete()
        return Response({
            "error": False, 
            "status": status.HTTP_204_NO_CONTENT,
            "message": "Xoa Ket Qua Chuyen Khoa Thanh Cong"
        })
    
    # TODO kết quả chuyên khoa sẽ query theo kết quả tổng quát, mỗi kết quả tổng quát sẽ có nhiều kết quả chuyên khoa

class DieuPhoiPhongChucNangView(views.APIView):

    def get_object(self, pk):
        try:
            return PhongChucNang.objects.get(pk=pk)
        except PhongChucNang.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        phong_chuc_nang = self.get_object(pk=pk)
        dich_vu_kham = phong_chuc_nang.dich_vu_kham
        chuoi_kham = dich_vu_kham.dich_vu_kham.all()
        serializer = ChuoiKhamSerializerSimple(chuoi_kham, many=True, context={"request": request})
        return Response(serializer.data)

class FileKetQuaViewSet(viewsets.ModelViewSet):
    serializer_class = FileKetQuaSerializer
    queryset = FileKetQua.objects.all()


class ListNguoiDungDangKiKham(APIView):
    def get(self, request, format=None):
        queryset = LichHenKham.objects.select_related('benh_nhan').filter(trang_thai=4)
        serializer = LichHenKhamSerializer(queryset, many=True, context={'request': request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "data": serializer.data
        }
        return Response(response)

class ChuoiKhamNguoiDung(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            chuoi_kham = ChuoiKham.objects.select_related('benh_nhan').filter(benh_nhan=user_id)
            serializer = ChuoiKhamSerializerSimple(chuoi_kham, many=True, context={"request": request})
            response = {
                "error": False,
                "status": status.HTTP_200_OK,
                "data": serializer.data
            }
            return Response(response)

class DanhSachThuocTheoCongTy(APIView):
    def get(self, request, format=None):
        id_cong_ty = self.request.query_params.get('id_cong_ty', None)
        if id_cong_ty:
            thuoc = Thuoc.objects.select_related('cong_ty').filter(cong_ty = id_cong_ty)
            serializer = ThuocSerializer(thuoc, many=True, context={"request":request})
            response = {
                "error" : False,
                "status" : status.HTTP_200_OK,
                "data" : serializer.data
            }
            return Response(response)
class DanhSachBenhNhanTheoPhong(APIView):
    def get(self, request, format=None):
        id_phong = self.request.query_params.get('id_phong', None)
        if id_phong:
            phong_chuc_nang = get_object_or_404(PhongChucNang, id=id_phong)
            # dich_vu_kham = 
            chuyen_khoa_kham = phong_chuc_nang.dich_vu_kham
            ds_phan_khoa_by_users = chuyen_khoa_kham.dich_vu_kham.all()
            serializer = PhanKhoaKhamSerializer(ds_phan_khoa_by_users, many=True, context={'request': request})
            response_data = {
                "error": False,
                "status": status.HTTP_200_OK,
                "data": serializer.data
            }
            return Response(response_data)
        # return Response({'key': serializer.data}, status=status.HTTP_200_OK)

# TODO Danh sách bệnh nhân theo phòng: nếu trạng thái chuỗi khám và phân khoa khám của bệnh nhân trở thành "Dừng Lại" thì sẽ filter exclude trạng thái "Dừng Lại"

class DanhSachDichVuKhamTheoPhong(APIView):
    def get(self, request, format=None):
        ten_phong_chuc_nang = self.request.query_params.get('ten_phong_chuc_nang')
        phong_chuc_nang = PhongChucNang.objects.filter(ten_phong_chuc_nang=ten_phong_chuc_nang)
        # dich_vu_kham = 
        danh_sach = PhanKhoaKham.objects.filter(dich_vu_kham__phong_chuc_nang_theo_dich_vu__ten_phong_chuc_nang=ten_phong_chuc_nang).distinct()

        serializer = PhanKhoaKhamSerializer(danh_sach, many=True, context={'request': request})
        # serializer = PhongChucNangSerializer(phong_chuc_nang, many=True, context={'request': request})
        response = {
            'data': serializer.data
        }
        return Response(response)

class DanhSachPhongChucNang(APIView):
    def get(self, request, format=None):
        phong_chuc_nang = PhongChucNang.objects.all()
        serializer = PhongChucNangSerializerSimple(phong_chuc_nang, many=True, context={"request": request})
        phong_chuc_nang_data = serializer.data
        return Response({"error":False, "message": "Danh Sach Phong Chuc Nang", "data": phong_chuc_nang_data})

        
class PhongChucNangTheoDichVu(APIView):
    def get(self, request, format=None):
        id_dich_vu = self.request.query_params.get('id_dich_vu', None)
        if id_dich_vu:
            dich_vu = get_object_or_404(DichVuKham, id=id_dich_vu)
            phong_chuc_nang = dich_vu.phong_chuc_nang_theo_dich_vu.all()
            data_phong = phong_chuc_nang[0]
            profile_phong_chuc_nang = data_phong.profile_phong_chuc_nang
            serializer = ProfilePhongChucNangSerializer(profile_phong_chuc_nang, context={'request': request})
            data = serializer.data
            # print(data)
            response_data = {
                'ten_phong_chuc_nang': data['phong_chuc_nang']['ten_phong_chuc_nang'],
                'so_luong_cho': data['so_luong_cho'],
                'thoi_gian_cho': data['thoi_gian_trung_binh'],
            }

            return Response(response_data)

class DanhSachHoaDonDichVu(APIView):
    def get(self, request, format=None):
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        trang_thai = TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham="Chờ Thanh Toán")[0]
        danh_sach_chuoi_kham = ChuoiKham.objects.select_related('benh_nhan').filter(trang_thai=trang_thai, thoi_gian_tao__lt=today_end)
        serializer = HoaDonChuoiKhamSerializerSimple(danh_sach_chuoi_kham, many=True, context={'request': request})
        data = serializer.data
        response_data = {
            'error': False, 
            'data': data
        }
        return Response(response_data)

class DanhSachHoaDonThuoc(APIView):
    def get(self, request, format=None):
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        trang_thai = TrangThaiDonThuoc.objects.get_or_create(trang_thai = "Chờ Thanh Toán")[0]
        danh_sach_don_thuoc = DonThuoc.objects.select_related('benh_nhan').filter(trang_thai=trang_thai, thoi_gian_tao__lt=today_end)
        serializer = HoaDonThuocSerializerSimple(danh_sach_don_thuoc, many=True, context={'request': request})
        data = serializer.data
        response_data = {
            'error': False, 
            'data': data
        }
        return Response(response_data)
        
class DanhSachDonThuocPhongThuoc(APIView):
    def get(self, request, format=None):
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        # trang_thai = TrangThaiDonThuoc.objects.filter(Q(trang_thai = "Chờ Thanh Toán") | Q(trang_thai = "Đã Thanh Toán"))
        trang_thai = TrangThaiDonThuoc.objects.get_or_create(trang_thai = "Đã Thanh Toán")[0]
        danh_sach_don_thuoc = DonThuoc.objects.filter(trang_thai=trang_thai, thoi_gian_tao__lt=today_end)
        serializer = HoaDonThuocSerializerSimple(danh_sach_don_thuoc, many=True, context={'request': request})
        data = serializer.data
        response_data = {
            'error': False, 
            'data': data
        }
        return Response(response_data)

class DanhSachDonThuocDaKe(APIView):
    def get(self, request, format=None):
        trang_thai = TrangThaiDonThuoc.objects.get_or_create(trang_thai="Chờ Thanh Toán")[0]
        danh_sach_don_thuoc = DonThuoc.objects.select_related('benh_nhan').filter(trang_thai=trang_thai)
        serializer = HoaDonThuocSerializerSimple(danh_sach_don_thuoc, many=True, context={'request': request})
        data = serializer.data
        response_data = {
            'error': False, 
            'data': data
        }
        return Response(response_data)

class DanhSachThanhToanLamSang(APIView):
    def get(self, request, format=None):
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Chờ Thanh Toán Lâm Sàng")[0]
        danh_sach_lam_sang = LichHenKham.objects.select_related('benh_nhan').filter(trang_thai = trang_thai, thoi_gian_tao__lt=today_end)
        serializer = LichHenKhamSerializer(danh_sach_lam_sang, many=True, context={'request': request})
        data = serializer.data
        response_data = {
            'error': False, 
            'data': data,
        }
        return Response(response_data)
class ThongTinPhongChucNang(APIView):
    def get(self, request, format=None):
        id_dich_vu = self.request.query_params.get('id_dich_vu', None)
        if id_dich_vu:
            dich_vu = get_object_or_404(DichVuKham, id=id_dich_vu)
            phong_chuc_nang = dich_vu.phong_chuc_nang_theo_dich_vu.all()
            if len(phong_chuc_nang) == 0:
                response = {
                    'status': 400,
                    'message': "Không Tìm Thấy Thông Tin"
                }
                return Response(response)
            trang_thai_cho = TrangThaiKhoaKham.objects.get_or_create(trang_thai_khoa_kham='Đang chờ')[0]
            trang_thai_thuc_hien = TrangThaiKhoaKham.objects.get_or_create(trang_thai_khoa_kham='Đang Thực Hiện')[0]
            ds_benh_nhan = dich_vu.dich_vu_kham.select_related().filter(Q(trang_thai=trang_thai_cho) | Q(trang_thai=trang_thai_thuc_hien))
            ds_benh_nhan_dang_cho = dich_vu.dich_vu_kham.select_related().filter(trang_thai=trang_thai_cho)
            ds_benh_nhan_dang_thuc_hien = dich_vu.dich_vu_kham.select_related().filter(trang_thai=trang_thai_thuc_hien)
            if len(ds_benh_nhan) == 0:
                response = {
                    'status': 400,
                    'message': "Không Tìm Thấy Thông Tin"
                }
                return Response(response)
            so_luong = ds_benh_nhan.count()
            so_luong_cho = ds_benh_nhan_dang_cho.count()
            so_luong_thuc_hien = ds_benh_nhan_dang_thuc_hien.count()
            data_phong = phong_chuc_nang[0]
            open_div = "<div class='text-left'>"
            close_div = "</div>"
            html_ten_phong = f"<span class='head'>Phòng : </span><span>{data_phong.ten_phong_chuc_nang}</span><br/>"
            html_so_luong = f"<span class='head'>Tổng Số Người : </span><span>{so_luong}</span><br/>"
            html_so_luong_dang_cho = f"<span class='head'>Đang Chờ : </span><span>{so_luong_cho}</span><br/>"
            html_so_luong_dang_thuc_hien = f"<span class='head'>Đang Thực Hiện : </span><span>{so_luong_thuc_hien}</span><br/>"
            html = open_div + html_ten_phong + html_so_luong + html_so_luong_dang_cho + html_so_luong_dang_thuc_hien + close_div
            response_data = {
                'status': 200,
                'html': str(html)
            }
            
            return Response(response_data)

class DanhSachKhamTrongNgay(APIView):
    def get(self, request, format=None):
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        # cho_thanh_toan = TrangThaiChuoiKham.objects.get(trang_thai_chuoi_kham="Chờ Thanh Toán")
        cho_thanh_toan = TrangThaiChuoiKham.objects.get(trang_thai_chuoi_kham="Chờ Thanh Toán")
        da_thanh_toan = TrangThaiChuoiKham.objects.get(trang_thai_chuoi_kham='Đã Thanh Toán')
        # dang_thuc_hien = TrangThaiChuoiKham.objects.get(trang_thai_chuoi_kham="Đang Thực Hiện")
        dang_thuc_hien = TrangThaiChuoiKham.objects.get(trang_thai_chuoi_kham="Đang Thực Hiện")
        hoan_thanh = TrangThaiChuoiKham.objects.get(trang_thai_chuoi_kham="Hoàn Thành")

        ds_benh_nhan = ChuoiKham.objects.select_related('benh_nhan').filter(thoi_gian_tao__lt=today_end).filter(Q(trang_thai=cho_thanh_toan) | Q(trang_thai=da_thanh_toan) | Q(trang_thai=dang_thuc_hien) | Q(trang_thai=hoan_thanh))

        serializer = ChuoiKhamSerializerSimple(ds_benh_nhan, many=True, context={'request': request})
        data = serializer.data
        response_data = {
            'error': False,
            'data': data,
        }
        return Response(response_data)

class DanhSachPhongChucNang(APIView):
    def get(self, request, format=None):

        phong_chuc_nang = PhongChucNang.objects.all()
        serializer = PhongChucNangSerializerSimple(phong_chuc_nang, many=True, context={"request": request})
        phong_chuc_nang_data = serializer.data
        return Response({"error":False, "message": "Danh Sach Phong Chuc Nang", "data": phong_chuc_nang_data})
        
# UPDATE NGAY 4/1
class DanhSachDoanhThuDichVu(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)

        start = datetime.strptime(range_start, "%d-%m-%Y")
        tomorrow_start = start + timedelta(1)
        
        if range_end == '':
            danh_sach_dich_vu = HoaDonChuoiKham.objects.filter(Q(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gte=start) | Q(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gte=start))

            serializer = HoaDonChuoiKhamSerializer(danh_sach_dich_vu, many=True, context={'request': request})
            data = serializer.data

            return Response(data)
        else: 
            end = datetime.strptime(range_end, "%d-%m-%Y")
            tomorrow_end = end + timedelta(1)

            danh_sach_dich_vu = HoaDonChuoiKham.objects.filter(Q(thoi_gian_tao__lt=tomorrow_end, thoi_gian_tao__gte=start) | Q(thoi_gian_tao__lt=end, thoi_gian_tao__gte=start))

            serializer = HoaDonChuoiKhamSerializer(danh_sach_dich_vu, many=True, context={'request': request})
            data = serializer.data

            return Response(data)

class DanhSachDoanhThuLamSang(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)

        start = datetime.strptime(range_start, "%d-%m-%Y")
        tomorrow_start = start + timedelta(1)
        
        if range_end == '':
            danh_sach_hoa_don = HoaDonLamSang.objects.filter(Q(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gte=start) | Q(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gte=start))

            serializer = HoaDonLamSangSerializer(danh_sach_hoa_don, many=True, context={'request': request})
            data = serializer.data

            return Response(data)
        else: 
            end = datetime.strptime(range_end, "%d-%m-%Y")
            tomorrow_end = end + timedelta(1)

            danh_sach_hoa_don = HoaDonLamSang.objects.filter(Q(thoi_gian_tao__lt=tomorrow_end, thoi_gian_tao__gte=start) | Q(thoi_gian_tao__lt=end, thoi_gian_tao__gte=start))

            serializer = HoaDonLamSangSerializer(danh_sach_hoa_don, many=True, context={'request': request})
            data = serializer.data

            return Response(data)

class DanhSachDoanhThuThuoc(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)

        start = datetime.strptime(range_start, "%d-%m-%Y")
        tomorrow_start = start + timedelta(1)
        
        if range_end == '':
            danh_sach_hoa_don_thuoc = HoaDonThuoc.objects.filter(Q(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gte=start) | Q(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gte=start))

            serializer = HoaDonThuocSerializer(danh_sach_hoa_don_thuoc, many=True, context={'request': request})
            data = serializer.data

            return Response(data)
        else: 
            end = datetime.strptime(range_end, "%d-%m-%Y")
            tomorrow_end = end + timedelta(1)

            danh_sach_hoa_don_thuoc = HoaDonThuoc.objects.filter(Q(thoi_gian_tao__lt=tomorrow_end, thoi_gian_tao__gte=start) | Q(thoi_gian_tao__lt=end, thoi_gian_tao__gte=start))

            serializer = HoaDonThuocSerializer(danh_sach_hoa_don_thuoc, many=True, context={'request': request})
            data = serializer.data

            return Response(data)
    # END UPDATE 
class DanhSachBenhNhan(APIView):
    def get(self, request, format=None):
        danh_sach_benh_nhan = User.objects.filter(chuc_nang = 1)
        
        serializer = UserSerializer(danh_sach_benh_nhan, many=True, context={'request': request})
        data = serializer.data
        
        return Response(data)

from datetime import datetime, timedelta

class ThongTinBenhNhanTheoMa(APIView):
    def get(self, request, format = None):
        ma_benh_nhan = self.request.query_params.get('ma_benh_nhan')
        thong_tin_theo_ma = User.objects.get(id = ma_benh_nhan)

        serializer = UserSerializer(thong_tin_theo_ma, context={'request': request})

        data = {
            'thong_tin_theo_ma': serializer.data
        }

        return HttpResponse(json.dumps(data), content_type="application/json, charset=utf-8")
        # serializer = UserSerializer()


class DanhSachLichHenTheoBenhNhan(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)

        start = datetime.strptime(range_start, "%d-%m-%Y")
        tomorrow_start = start + timedelta(1)

        if range_end == '':
            lich_hen = LichHenKham.objects.select_related('benh_nhan').filter(Q(thoi_gian_bat_dau__lt=tomorrow_start, thoi_gian_ket_thuc__gte=start) | Q(thoi_gian_bat_dau__lt=tomorrow_start, thoi_gian_bat_dau__gte=start))

        else:
            end = datetime.strptime(range_end, "%d-%m-%Y")
            tomorrow_end = end + timedelta(1)
            lich_hen = LichHenKham.objects.select_related('benh_nhan').filter(Q(thoi_gian_bat_dau__lt=end, thoi_gian_ket_thuc__gte=start) | Q(thoi_gian_bat_dau__lt=tomorrow_end, thoi_gian_bat_dau__gte=start))
            
        serializer = LichHenKhamSerializer(lich_hen, many=True, context={'request': request})

        data = serializer.data
        return Response(data)

class DanhSachDoanhThuTheoThoiGian(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)

        start = datetime.strptime(range_start, "%d-%m-%Y")
        # today_end = datetime.strptime(today_end, "%d-%m-%Y")
        tomorrow_start = start + timedelta(1)

        # print(start)
        if range_end == '':
            tong_tien_hoa_don_chuoi_kham_theo_thoi_gian = HoaDonChuoiKham.objects.filter( thoi_gian_tao__gt=start, thoi_gian_tao__lt=tomorrow_start).exclude(tong_tien__isnull=True).annotate(day=TruncDay("thoi_gian_tao")).values("day").annotate(c=Count("id")).annotate(total_spent=Sum(F("tong_tien")))
            print(tong_tien_hoa_don_chuoi_kham_theo_thoi_gian)
            list_tong_tien = [x['total_spent'] for x in tong_tien_hoa_don_chuoi_kham_theo_thoi_gian]
            tong_tien_dich_vu_kham = sum(list_tong_tien)

            tong_tien_lam_sang_theo_thoi_gian = HoaDonLamSang.objects.filter(thoi_gian_tao__gt=start, thoi_gian_tao__lt=tomorrow_start).exclude(tong_tien__isnull=True).annotate(day=TruncDay("thoi_gian_tao")).values("day").annotate(c=Count("id")).annotate(total_spent=Sum(F("tong_tien")))
            list_tong_tien_lam_sang = [x['total_spent'] for x in tong_tien_lam_sang_theo_thoi_gian]
            tong_tien_lam_sang = sum(list_tong_tien_lam_sang)

            tong_tien_dich_vu = tong_tien_dich_vu_kham + tong_tien_lam_sang

            tong_tien_hoa_don_thuoc_theo_thoi_gian = HoaDonThuoc.objects.filter( thoi_gian_tao__gt=start, thoi_gian_tao__lt=tomorrow_start).exclude(tong_tien__isnull=True).annotate(day=TruncDay("thoi_gian_tao")).values("day").annotate(c=Count("id")).annotate(total_spent=Sum(F("tong_tien")))
            list_tong_tien_don_thuoc = [x['total_spent'] for x in tong_tien_hoa_don_thuoc_theo_thoi_gian]
            print(list_tong_tien_don_thuoc)
            tong_tien_don_thuoc = sum(list_tong_tien_don_thuoc)

            tong_doanh_thu = tong_tien_dich_vu + tong_tien_don_thuoc
            response = [
                {
                    'loai_doanh_thu'    : 'Tong Doanh Thu',
                    'thoi_gian_bat_dau' : start,
                    'thoi_gian_ket_thuc': tomorrow_start,
                    'tong_tien'         : tong_doanh_thu
                },
                {
                    'loai_doanh_thu'    : 'Tong Doanh Thu Dich Vu',
                    'thoi_gian_bat_dau' : start,
                    'thoi_gian_ket_thuc': tomorrow_start,
                    'tong_tien'         : tong_tien_dich_vu
                },
                {
                    'loai_doanh_thu'    : 'Tong Doanh Thu Thuoc',
                    'thoi_gian_bat_dau' : start,
                    'thoi_gian_ket_thuc': tomorrow_start,
                    'tong_tien'         : tong_tien_don_thuoc
                },
                
            ]
            return Response(response)

        else:
            end = datetime.strptime(range_end, "%d-%m-%Y")
            # tomorrow_end = end + timedelta(1)
            
            tong_tien_hoa_don_chuoi_kham_theo_thoi_gian = HoaDonChuoiKham.objects.filter( thoi_gian_tao__gt=start, thoi_gian_tao__lt=end).exclude(tong_tien__isnull=True).annotate(day=TruncDay("thoi_gian_tao")).values("day").annotate(c=Count("id")).annotate(total_spent=Sum(F("tong_tien")))
            print(tong_tien_hoa_don_chuoi_kham_theo_thoi_gian)
            list_tong_tien = [x['total_spent'] for x in tong_tien_hoa_don_chuoi_kham_theo_thoi_gian]
            tong_tien_dich_vu_kham = sum(list_tong_tien)
            print(tong_tien_dich_vu_kham)

            tong_tien_lam_sang_theo_thoi_gian = HoaDonLamSang.objects.filter(thoi_gian_tao__gt=start, thoi_gian_tao__lt=end).exclude(tong_tien__isnull=True).annotate(day=TruncDay("thoi_gian_tao")).values("day").annotate(c=Count("id")).annotate(total_spent=Sum(F("tong_tien")))
            list_tong_tien_lam_sang = [x['total_spent'] for x in tong_tien_lam_sang_theo_thoi_gian]
            tong_tien_lam_sang = sum(list_tong_tien_lam_sang)

            tong_tien_dich_vu = tong_tien_dich_vu_kham + tong_tien_lam_sang

            tong_tien_hoa_don_thuoc_theo_thoi_gian = HoaDonThuoc.objects.filter( thoi_gian_tao__gt=start, thoi_gian_tao__lt=end).exclude(tong_tien__isnull=True).annotate(day=TruncDay("thoi_gian_tao")).values("day").annotate(c=Count("id")).annotate(total_spent=Sum(F("tong_tien")))
            list_tong_tien_don_thuoc = [x['total_spent'] for x in tong_tien_hoa_don_thuoc_theo_thoi_gian]
            print(list_tong_tien_don_thuoc)
            tong_tien_don_thuoc = sum(list_tong_tien_don_thuoc)

            tong_doanh_thu = tong_tien_dich_vu + tong_tien_don_thuoc
            response = [
                {
                    'loai_doanh_thu': 'Tong Doanh Thu',
                    'thoi_gian_bat_dau': start,
                    'thoi_gian_ket_thuc': end,
                    'tong_tien': tong_doanh_thu
                },
                {
                    'loai_doanh_thu': 'Tong Doanh Thu Dich Vu',
                    'thoi_gian_bat_dau': start,
                    'thoi_gian_ket_thuc': end,
                    'tong_tien': tong_tien_dich_vu
                },
                {
                    'loai_doanh_thu': 'Tong Doanh Thu Thuoc',
                    'thoi_gian_bat_dau': start,
                    'thoi_gian_ket_thuc': end,
                    'tong_tien': tong_tien_don_thuoc
                },
                
            ]
            return Response(response)
        return HttpResponse('okay')

class SetChoThanhToan(APIView):
    def get(self, request, format=None):
        id = self.request.query_params.get('id', None)
        user = request.user
        lich_hen = LichHenKham.objects.filter(id = id)[0]
        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Chờ Thanh Toán Lâm Sàng")[0]

        lich_hen.trang_thai = trang_thai
        lich_hen.nguoi_phu_trach = user
        lich_hen.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"first_process_user_{lich_hen.benh_nhan.id}", {
                'type':'first_process_notification',
            }
        )

        data = {
            "message" : "Thay đổi trạng thái thành công!"
        }

        return HttpResponse(json.dumps(data), content_type="application/json, charset=utf-8")

class SetXacNhanKham(APIView):
    def get(self, request, format=None):
        id = self.request.query_params.get('id', None)
        user = request.user
        lich_hen = LichHenKham.objects.filter(id = id)[0]
        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Xác Nhận")[0]

        lich_hen.trang_thai = trang_thai
        lich_hen.nguoi_phu_trach = user
        lich_hen.save()

        data = {
            "message" : "Thay đổi trạng thái thành công"
        }

        return HttpResponse(json.dumps(data), content_type="application/json, charset=utf-8")

# class DanhSachKetQuaKhamChuyenKhoa(APIView):
#     def get(self, request, format=None):
#         id = self.request.query_params.get('id', None)

#         ket_qua_chuyen_khoa = KetQuaChuyenKhoa.objects.get(id)
        
# class HoaDonTongTheoNguoiDung(APIView):
#     def get(self, request, format = None)
#         benh_nhan
class PhanKhoaKhamBenhNhan(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        user = User.objects.get(id=user_id)
        
        chuoi_kham = ChuoiKham.objects.filter(benh_nhan=user, thoi_gian_tao__lt=today_end, thoi_gian_tao__gte=today_start).order_by('-thoi_gian_tao').first()
        if chuoi_kham:
            danh_sach_phan_khoa = chuoi_kham.phan_khoa_kham.all()
            # serializer = DanhSachPhanKhoaSerializer(danh_sach_phan_khoa, many=True, context={'request': request})
            serializer = DanhSachPhanKhoaSerializer(danh_sach_phan_khoa, many=True, context={'request': request})
            data = serializer.data
            response = {
                'benh_nhan': user_id,
                'data': data
            }
            return Response(response)
        else:
            response = {
                'benh_nhan': user_id,
                'data': []
              
            }
            return Response(response)
 
class DanhSachChuoiKhamBenhNhan(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        user = User.objects.get(id=user_id)
        danh_sach_lich_hen = user.benh_nhan_hen_kham.all()
        serializer = LichHenKhamUserSerializer(danh_sach_lich_hen, many=True, context={'request': request})
        response = {
            'benh_nhan': user_id,
            'data': serializer.data
        }
        return Response(response)

class ChuoiKhamGanNhat(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        user = User.objects.get(id=user_id)
        
        chuoi_kham = ChuoiKham.objects.filter(benh_nhan=user, thoi_gian_tao__lt=today_end, thoi_gian_tao__gte=today_start).order_by('-thoi_gian_tao').first()
        if chuoi_kham:
            serializer = ChuoiKhamSerializerSimple(chuoi_kham, context={'request': request})

            response = {
                "data": serializer.data,
            }
            return Response(response)
        else:
            response = {
                "data": '',
            }
            return Response(response)
        # return Response({'message': 'Loi'})
 
class KetQuaChuoiKhamBenhNhan(APIView):
    def get(self, request, format=None):
        chuoi_kham_id = self.request.query_params.get('id_chuoi_kham')
        chuoi_kham = ChuoiKham.objects.get(id=chuoi_kham_id)
        ket_qua_tong_quat = chuoi_kham.ket_qua_tong_quat.all()
        serializer = KetQuaTongQuatSerializer(ket_qua_tong_quat, many=True, context={'request': request})
        response = {
            'chuoi_kham': chuoi_kham_id,
            'data': serializer.data
        }
        return Response(response)

class KetQuaChuoiKhamBenhNhan2(APIView):
    def get(self, request, format=None):
        chuoi_kham_id = self.request.query_params.get('id_chuoi_kham')
        chuoi_kham = ChuoiKham.objects.get(id=chuoi_kham_id)
        ket_qua_tong_quat = chuoi_kham.ket_qua_tong_quat.all()[0]
        ket_qua_chuyen_khoa = ket_qua_tong_quat.ket_qua_chuyen_khoa.all()
        serializer = KetQuaChuyenKhoaSerializer(ket_qua_chuyen_khoa, many=True, context={'request': request})
        response = {
            'chuoi_kham': chuoi_kham_id,
            'data': serializer.data
        }
        return Response(response)
 
class DanhSachDonThuocBenhNhan(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        user = User.objects.get(id = user_id)
        danh_sach_don_thuoc = user.don_thuoc.all()
        serializer = DanhSachDonThuocSerializer(danh_sach_don_thuoc, many=True, context={'request': request})
        response = {
            'benh_nhan': user_id,
            'data': serializer.data
        }
        return Response(response)

class DanhSachThuocBenhNhan(APIView):
    def get(self, request, format=None):
        don_thuoc_id = self.request.query_params.get('don_thuoc_id')
        don_thuoc = DonThuoc.objects.get(id=don_thuoc_id)
        danh_sach_thuoc = don_thuoc.ke_don.all()
        serializer = KeDonThuocSerializer(danh_sach_thuoc, many=True, context={'request': request})
        response = {
            'don_thuoc': int(don_thuoc_id),
            'data': serializer.data
        }
        return Response(response)
        # return HttpResponse(json.dumps(response, cls=UUIDEncoder))
 
# class DichVuKhamTheoPhongChucNang(APIView):
#     def get(request, self, format=None):
#         phong_chuc_nang = PhongChucNangSerializerSimple()
#         dich_vu_kham = DichVuKham.objects.all()

class DanhSachThuocHienTai(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        user = User.objects.get(id=user_id)
        don_thuoc = DonThuoc.objects.filter(benh_nhan=user, thoi_gian_tao__lt=today_end, thoi_gian_tao__gte=today_start).order_by("-thoi_gian_tao").first()
        if don_thuoc:
            danh_sach_thuoc = don_thuoc.ke_don.all()
            serializer = KeDonThuocSerializer(danh_sach_thuoc, many=True, context={'request': request})
            response = {
                'don_thuoc': don_thuoc.id,
                'data': serializer.data
            }
        else:
            response = {
                'don_thuoc': "",
                'data': []
            }
        return Response(response)

class DanhSachBenhNhanTheoPhongChucNang(APIView):
    def get(self, request, format=None):
        id_phong = self.request.query_params.get('id')
        phong = PhongChucNang.objects.get(id=id_phong)
        danh_sach_dich_vu = phong.dich_vu_kham_theo_phong.all()

        danh_sach_phan_khoa = set()
        for dich_vu in danh_sach_dich_vu:
            for phan_khoa in dich_vu.phan_khoa_dich_vu.all():
                if phan_khoa:
                    if phan_khoa.chuoi_kham.trang_thai.trang_thai_chuoi_kham == 'Đang Thực Hiện' or phan_khoa.chuoi_kham.trang_thai.trang_thai_chuoi_kham == 'Đã Thanh Toán':
                        danh_sach_phan_khoa.add(phan_khoa)
        
        serializer = PhanKhoaKhamSerializer(danh_sach_phan_khoa, many=True, context={'request': request})

        response = {
            'data': serializer.data,
        }
        return Response(response)
                
class DanhSachDichVuTheoPhongChucNang(APIView):
    def get(self, request, format=None):
        id_phong_chuc_nang = self.request.query_params.get('id_phong_chuc_nang', None)
        if id_phong_chuc_nang:
            dich_vu_kham = DichVuKham.objects.select_related('phong_chuc_nang').filter(phong_chuc_nang = id_phong_chuc_nang)
            serializer = DichVuKhamSerializer(dich_vu_kham, many=True, context={"request":request})
            response = {
                "error" : False,
                "status": status.HTTP_200_OK,
                "data"  : serializer.data
            }
            return Response(response)
        
class LichHenKhamSapToi(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        user = User.objects.get(id=user_id)
        now = timezone.now()
        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai="Xác Nhận")[0]
        try:
            lich_hen_kham = LichHenKham.objects.filter(benh_nhan=user).filter(trang_thai=trang_thai).annotate(timediff=F('thoi_gian_bat_dau')).order_by('timediff')[0]
            
            if lich_hen_kham:
                # print(lich_hen_kham.thoi_gian_bat_dau)
                # if lich_hen_kham.thoi_gian_bat_dau <= now:
                #    return Response({'data': []})
                serializer = LichHenKhamSerializer(lich_hen_kham, context={'request': request})
                response = {
                    'data': serializer.data
                }
                return Response(response)
            else:
                response = {
                    'data': []
                }
                return Response(response)
        except :
            return Response({'data': []})
        
class DonThuocGanNhat(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get("user_id")
        user = User.objects.get(id=user_id)
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        user = User.objects.get(id=user_id)
        
        
        don_thuoc = DonThuoc.objects.filter(benh_nhan=user, thoi_gian_tao__lt=today_end, thoi_gian_tao__gte=today_start).order_by("-thoi_gian_tao").first()
        if don_thuoc:
            serializer = DonThuocSerializer(don_thuoc, context={'request': request})
            response = {
                'data': serializer.data
            }
            return Response(response)
        else:
            response = {
                'data': ''
            }
            return Response(response)

class TatCaLichHenBenhNhan(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        user = User.objects.get(id=user_id)
        now = timezone.localtime(timezone.now())
        trang_thai = TrangThaiLichHen.objects.get_or_create(
            ten_trang_thai='Xác Nhận')[0]
        trang_thai_dat_truoc = TrangThaiLichHen.objects.get_or_create(
            ten_trang_thai='Đã Đặt Trước')[0]

        lich_hen = LichHenKham.objects.filter(benh_nhan=user).filter(Q(trang_thai=trang_thai) | Q(trang_thai=trang_thai_dat_truoc)).annotate(relevance=models.Case(
            models.When(thoi_gian_bat_dau__gte=now, then=1),
            models.When(thoi_gian_bat_dau__lt=now, then=2),
            output_field=models.IntegerField(),
        )).annotate(
            timediff=models.Case(
                models.When(thoi_gian_bat_dau__gte=now,
                            then=F('thoi_gian_bat_dau') - now),
                models.When(thoi_gian_bat_dau__lt=now,
                            then=now - F('thoi_gian_bat_dau')),
                # models.When(thoi_gian_bat_dau__lte=today_end - F('thoi_gian_bat_dau')),
                output_field=models.DurationField(),
            )).order_by('relevance', 'timediff')

        upcoming_events = []
        past_events = []
        for lich in lich_hen:
            if lich.relevance == 1:
                upcoming_events.append(lich)
            elif lich.relevance == 2:
                past_events.append(lich)

        serializer_1 = LichHenKhamSerializer(
            upcoming_events, many=True, context={'request': request})
        serializer_2 = LichHenKhamSerializer(
            past_events, many=True, context={'request': request})
        response = {
            'benh_nhan': user_id,
            'upcoming': serializer_1.data,
            'past': serializer_2.data,
        }

        return Response(response)

class DangKiLichHen(APIView):
    def post(self, request, format=None):
        serializer = BookLichHenKhamSerializer(data=request.data)

        if serializer.is_valid():
            user_id = serializer.validated_data['benh_nhan']
            thoi_gian_bat_dau = serializer.validated_data['thoi_gian_bat_dau']
            loai_dich_vu = serializer.validated_data['loai_dich_vu']
            ly_do = serializer.validated_data['ly_do']
            dia_diem = serializer.validated_data['dia_diem']
            
            user = User.objects.get(id=user_id)
            date_time_str = datetime.strptime(thoi_gian_bat_dau, '%Y-%m-%d %H:%M:%S')
            trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai='Đã Đặt Trước')[0]
            lich_hen = LichHenKham.objects.create(
                benh_nhan=user,
                thoi_gian_bat_dau=date_time_str, 
                trang_thai=trang_thai,
                dia_diem=dia_diem,
                loai_dich_vu=loai_dich_vu,
                ly_do=ly_do,
                
            )
            serializer_1 = LichHenKhamSerializerSimple(lich_hen, context={'request': request})
            serializer_2 = UserSerializer(user, context={'request': request})
            response = {
                'benh_nhan': serializer_2.data,
                'lich_hen': serializer_1.data,
            }
        else:
            response = {
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'benh_nhan': "",
                'lich_hen': ''
            }
        return Response(response)

class UserInfor(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user, context={'request': request})
        response = {
            'user': serializer.data
        }
        return Response(response)

class DanhSachBacSi(APIView):
    def get(self, request, format=None):
        danh_sach_bac_si = User.objects.filter(Q(chuc_nang = 4) | Q(chuc_nang = 3))
        if len(danh_sach_bac_si) == 0: 
            response = {
            'data': []
        }
        else:
            serializer = UserSerializer(danh_sach_bac_si, many=True, context={'request': request})
            response = {
                'data': serializer.data
            }
        return Response(response)


class DanhSachBaiDang(APIView):
    def get(self, request, format=None):
        danh_sach_bai_dang = BaiDang.objects.all()
        print(danh_sach_bai_dang)

        serializer = BaiDangSerializer(danh_sach_bai_dang, many=True, context = {'request':request})
        data = serializer.data
        response = {
            'data': data
        }
        return Response(response)

class DanhSachDichVu(APIView):
    def get(self, request, format=None):
        danh_sach_dich_vu = DichVuKham.objects.all()
        serializer = DichVuKhamSerializer(danh_sach_dich_vu, many=True, context={'request': request})
        return Response(serializer.data)

class DichVuKhamPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000

# class PaginatedDichVuKhamListView(generics.ListAPIView):
#     queryset = DichVuKham.objects.all()
#     serializer_class = DichVuKhamSerializerSimple
#     pagination_class = DichVuKhamPagination

class DanhSachPhongChucNang(APIView):
    def get(self, request, format=None):   
        ds = PhongChucNang.objects.all()
        serializer = PhongChucNangSerializerSimple(ds, many=True, context={'request': request})
        response = {
            'data': serializer.data
        }
        return Response(response)
        
class DanhSachVatTu(APIView):
    def get(self, request, format=None):
        vat_tu = VatTu.objects.all()
        serializer = VatTuSerializer(vat_tu, many=True, context={'request': request})
        response = {
            'data' : serializer.data
        }
        return Response(response)
        
        
#------ MINH Update--------

class UserUpdateInfo(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            serializer = UserUpdateInfoSerializer(
                user, context={'request': request})
            data = serializer.data
            response = {
                'status': status.HTTP_200_OK,
                'data': data
            }
        except:
            response = {
                'status': status.HTTP_404_NOT_FOUND,
                'data': ''
            }
        return Response(response)


class UserUpdateInfoRequest(APIView):
    def patch(self, request, format=None):
        serializer = UserUpdateInfoRequestSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['benh_nhan']
            ho_ten = serializer.validated_data['ho_ten']
            so_dien_thoai = serializer.validated_data['so_dien_thoai']
            email = serializer.validated_data['email']
            cmnd_cccd = serializer.validated_data['cmnd_cccd']
            ngay_sinh = serializer.validated_data['ngay_sinh']
            gioi_tinh = serializer.validated_data['gioi_tinh']
            dia_chi = serializer.validated_data['dia_chi']
            dan_toc = serializer.validated_data['dan_toc']
            ma_so_bao_hiem = serializer.validated_data['ma_so_bao_hiem']
            try:
                user = User.objects.get(id=user_id)
                user.ho_ten = ho_ten
                user.so_dien_thoai = so_dien_thoai
                user.email = email
                user.cmnd_cccd = cmnd_cccd
                user.ngay_sinh = ngay_sinh
                user.gioi_tinh = gioi_tinh
                user.dia_chi = dia_chi
                user.dan_toc = dan_toc
                user.ma_so_bao_hiem = ma_so_bao_hiem
                user.save()

                response = {
                    'status': status.HTTP_200_OK,
                    'message': "Cập Nhật Thông Tin Cá Nhân Thành Công"
                }

            except User.DoesNotExist:
                response = {
                    'status': status.HTTP_404_NOT_FOUND,
                    'message': "Người Dùng Không Tồn Tại"
                }
        else:
            response = {
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': "Bạn Vui Lòng Nhập Đầy Đủ Thông Tin"
            }
        return Response(response)


class ImageUploadParser(FileUploadParser):
    media_type = 'image/*'


class UploadAvatarView(APIView):
    parser_classes = (MultiPartParser,)

    def put(self, request, format=None):
        id = request.GET.get('id')
        file = request.FILES.get('file')

        user = User.objects.get(id=id)
        user.anh_dai_dien = file
        user.save()

        return Response({'message': "oke"})


class UpdateAppointmentDetail(APIView):
    def get(self, request, format=None):
        appointment_id = self.request.query_params.get('appointment_id')

        try:
            lich_hen = LichHenKham.objects.get(id=appointment_id)
            serializer = AppointmentUpdateDetailSerializer(
                lich_hen, context={'request': request})
            response = {
                'status': status.HTTP_200_OK,
                'message': 'Thông Tin Lịch Khám',
                'data': serializer.data,
            }
        except LichHenKham.DoesNotExist:
            response = {
                'status': status.HTTP_404_NOT_FOUND,
                'message': 'Lịch Hẹn Không Tồn Tại',
                'data': '',
            }
        return Response(response)


class CapNhatLichHen(APIView):
    def post(self, request, format=None):
        serializer = UpdateLichHenKhamSerializer(data=request.data)

        if serializer.is_valid():
            lich_hen_id = serializer.validated_data['appointment_id']
            thoi_gian_bat_dau = serializer.validated_data['thoi_gian_bat_dau']
            loai_dich_vu = serializer.validated_data['loai_dich_vu']
            ly_do = serializer.validated_data['ly_do']
            dia_diem = serializer.validated_data['dia_diem']

            date_time_str = datetime.strptime(
                thoi_gian_bat_dau, '%Y-%m-%d %H:%M:%S')
            try:
                lich_hen = LichHenKham.objects.get(id=lich_hen_id)
                lich_hen.loai_dich_vu = loai_dich_vu
                lich_hen.ly_do = ly_do
                lich_hen.dia_diem = dia_diem
                lich_hen.thoi_gian_bat_dau = date_time_str
                lich_hen.save()

                response = {
                    'status': status.HTTP_200_OK,
                    'message': 'Cập Nhật Lịch Hẹn Thành Công',
                }
            except LichHenKham.DoesNotExist:
                response = {
                    'status': status.HTTP_404_NOT_FOUND,
                    'message': 'Không Tìm Thấy Lịch Hẹn',
                }
        else:
            response = {
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'Bạn Vui Lòng Xem Lại',
            }
        return Response(response)


class HoaDonChuoiKhamNguoiDung(APIView):
    def get(self, request, format=None):
        chuoi_kham_id = self.request.query_params.get('id_chuoi_kham')
        chuoi_kham = ChuoiKham.objects.get(id=chuoi_kham_id)
        hoa_don_dich_vu = chuoi_kham.hoa_don_dich_vu
        phan_khoa_kham = chuoi_kham.phan_khoa_kham.all()
        tong_tien = []
        for khoa_kham in phan_khoa_kham:
            if khoa_kham.bao_hiem:
                # gia = khoa_kham.dich_vu_kham.don_gia * decimal.Decimal((1 - (khoa_kham.dich_vu_kham.bao_hiem_dich_vu_kham.dang_bao_hiem)/100))
                gia = khoa_kham.dich_vu_kham.don_gia
            else:
                gia = khoa_kham.dich_vu_kham.don_gia
            tong_tien.append(gia)
        total_spent = sum(tong_tien)
        tong_tien.clear()


class HoaDonChuoiKhamCanThanhToan(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get('user_id')
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        user = User.objects.get(id=user_id)

        try:
            chuoi_kham = ChuoiKham.objects.filter(
                benh_nhan=user, thoi_gian_tao__lt=today_end, thoi_gian_tao__gte=today_start).order_by('-thoi_gian_tao').first()

            danh_sach_phan_khoa = chuoi_kham.phan_khoa_kham.all()
            tong_tien = []
            bao_hiem = []
            for khoa_kham in danh_sach_phan_khoa:
                if khoa_kham.bao_hiem:
                    # gia = khoa_kham.dich_vu_kham.don_gia * decimal.Decimal((1 - (khoa_kham.dich_vu_kham.bao_hiem_dich_vu_kham.dang_bao_hiem)/100))
                    gia = khoa_kham.dich_vu_kham.don_gia
                    bao_hiem.append(gia)
                else:
                    gia = khoa_kham.dich_vu_kham.don_gia
                tong_tien.append(gia)
            total_spent = sum(tong_tien)
            tong_bao_hiem = sum(bao_hiem)
            thanh_tien = total_spent - tong_bao_hiem
            tong_tien.clear()
            bao_hiem.clear()
            serializer = HoaDonChuoiKhamThanhToanSerializer(
                danh_sach_phan_khoa, many=True, context={'request': request})
            response = {
                'tong_tien': float(total_spent),
                'ap_dung_bao_hiem': float(tong_bao_hiem),
                'thanh_tien': float(thanh_tien),
                'data': serializer.data,
            }
        except:
            response = {
                'tong_tien': '',
                'ap_dung_bao_hiem': '',
                'thanh_tien': '',
                'data': [],
            }

        return Response(response)


class HoaDonThuocCanThanhToan(APIView):
    def get(self, request, format=None):

        user_id = self.request.query_params.get("user_id")
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        user = User.objects.get(id=user_id)
        try:
            don_thuoc = DonThuoc.objects.filter(
                benh_nhan=user, thoi_gian_tao__lt=today_end, thoi_gian_tao__gte=today_start).order_by('-thoi_gian_tao').first()

            danh_sach_thuoc = don_thuoc.ke_don.all()
            bao_hiem = []
            tong_tien = []
            for thuoc_instance in danh_sach_thuoc:
                if thuoc_instance.bao_hiem:
                    gia = int(thuoc_instance.thuoc.don_gia_tt) * \
                        thuoc_instance.so_luong
                    bao_hiem.append(gia)
                else:
                    gia = int(thuoc_instance.thuoc.don_gia_tt) * \
                        thuoc_instance.so_luong
                tong_tien.append(gia)

            total_spent = sum(tong_tien)
            tong_bao_hiem = sum(bao_hiem)
            thanh_tien = total_spent - tong_bao_hiem
            bao_hiem.clear()
            tong_tien.clear()
            serializer = DanhSachThuocSerializer(danh_sach_thuoc, many=True, context={'request': request})
            response = {
                'tong_tien': int(total_spent),
                'ap_dung_bao_hiem': int(tong_bao_hiem),
                'thanh_tien': int(thanh_tien),
                'data': serializer.data,
            }
        except:
            response = {
                'tong_tien': '',
                'ap_dung_bao_hiem': '',
                'thanh_tien': '',
                'data': [],
            }
        return Response(response)
        
# * update themm

class DichVuTheoPhongChucNang(APIView):
    def get(self, request, format=None):
        id_phong_chuc_nang = self.request.query_params.get('id_phong')
        try:
            phong_chuc_nang = PhongChucNang.objects.get(id=id_phong_chuc_nang)
            danh_sach_dich_vu = phong_chuc_nang.dich_vu_kham_theo_phong.all()
            serializer = DanhSachDichVuSerializer(danh_sach_dich_vu, many=True, context={'request': request})
            response = {
                'status': status.HTTP_200_OK,
                'message': 'Danh Sách Dịch Vụ Khám Theo Phòng Chức Năng',
                'data': serializer.data,
            }
        except PhongChucNang.DoesNotExist:
            response = {
                'status': status.HTTP_404_NOT_FOUND,
                'message': 'Không Có Dữ Liệu',
                'data': [],
            }
        return Response(response)
        
#* update 25/12

class DonThuocCuaChuoiKham(APIView):
    def get(self, request, format=None):
        id_chuoi_kham = self.request.query_params.get('id_chuoi_kham')
        try:
            chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
            don_thuoc = chuoi_kham.don_thuoc_chuoi_kham.all()[0]
            danh_sach_thuoc = don_thuoc.ke_don.all()
    
            serializer = KeDonThuocSerializer(danh_sach_thuoc, many=True, context={'request': request})
            response = {
                'don_thuoc': don_thuoc.id,
                'data': serializer.data
            }
        except ChuoiKham.DoesNotExist:
            response = {
                'don_thuoc': "",
                'data': []
            }
        return Response(response)
        
class HoaDonThuocCuaChuoiKham(APIView):
    def get(self, request, format = None):
        id_chuoi_kham = self.request.query_params.get('id_chuoi_kham')
        try:
            chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
            don_thuoc = chuoi_kham.don_thuoc_chuoi_kham.all()[0]

            danh_sach_thuoc = don_thuoc.ke_don.all()
            bao_hiem = []
            tong_tien = []
            for thuoc_instance in danh_sach_thuoc:
                if thuoc_instance.bao_hiem:
                    gia = int(thuoc_instance.thuoc.don_gia_tt) * \
                        thuoc_instance.so_luong
                    bao_hiem.append(gia)
                else:
                    gia = int(thuoc_instance.thuoc.don_gia_tt) * \
                        thuoc_instance.so_luong
                tong_tien.append(gia)

            total_spent = sum(tong_tien)
            tong_bao_hiem = sum(bao_hiem)
            thanh_tien = total_spent - tong_bao_hiem
            bao_hiem.clear()
            tong_tien.clear()
            serializer = DanhSachThuocSerializer(danh_sach_thuoc, many=True, context={'request': request})
            response = {
                'tong_tien': total_spent,
                'ap_dung_bao_hiem': tong_bao_hiem,
                'thanh_tien': thanh_tien,
                'data': serializer.data,
            }
        except ChuoiKham.DoesNotExist:
            response = {
                'tong_tien': '',
                'ap_dung_bao_hiem': '',
                'thanh_tien': '',
                'data': [],
            }
        return Response(response)
        
class HoaDonDichVuCuaChuoiKham(APIView):
    def get(self, request, format=None):
        id_chuoi_kham = self.request.query_params.get('id_chuoi_kham')
        try:
            chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
            danh_sach_phan_khoa = chuoi_kham.phan_khoa_kham.all()
            tong_tien = []
            bao_hiem = []
            for khoa_kham in danh_sach_phan_khoa:
                if khoa_kham.bao_hiem:
                    # gia = khoa_kham.dich_vu_kham.don_gia * decimal.Decimal((1 - (khoa_kham.dich_vu_kham.bao_hiem_dich_vu_kham.dang_bao_hiem)/100))
                    gia = khoa_kham.dich_vu_kham.don_gia
                    bao_hiem.append(gia)
                else:
                    gia = khoa_kham.dich_vu_kham.don_gia
                tong_tien.append(gia)
            total_spent = sum(tong_tien)
            tong_bao_hiem = sum(bao_hiem)
            thanh_tien = total_spent - tong_bao_hiem
            tong_tien.clear()
            bao_hiem.clear()
            serializer = HoaDonChuoiKhamThanhToanSerializer(
                danh_sach_phan_khoa, many=True, context={'request': request})
            response = {
                'tong_tien': float(total_spent),
                'ap_dung_bao_hiem': float(tong_bao_hiem),
                'thanh_tien': float(thanh_tien),
                'data': serializer.data,
            }
        except ChuoiKham.DoesNotExist:
             response = {
                'tong_tien': '',
                'ap_dung_bao_hiem': '',
                'thanh_tien': '',
                'data': [],
            }
        return Response(response)

class HoaDonThuocCuaChuoiKham(APIView):
    def get(self, request, format = None):
        id_chuoi_kham = self.request.query_params.get('id_chuoi_kham')
        try:
            chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
            don_thuoc = chuoi_kham.don_thuoc_chuoi_kham.all()[0]

            danh_sach_thuoc = don_thuoc.ke_don.all()
            bao_hiem = []
            tong_tien = []
            for thuoc_instance in danh_sach_thuoc:
                if thuoc_instance.bao_hiem:
                    gia = int(thuoc_instance.thuoc.don_gia_tt) * \
                        thuoc_instance.so_luong
                    bao_hiem.append(gia)
                else:
                    gia = int(thuoc_instance.thuoc.don_gia_tt) * \
                        thuoc_instance.so_luong
                tong_tien.append(gia)

            total_spent = sum(tong_tien)
            tong_bao_hiem = sum(bao_hiem)
            thanh_tien = total_spent - tong_bao_hiem
            bao_hiem.clear()
            tong_tien.clear()
            serializer = DanhSachThuocSerializer(danh_sach_thuoc, many=True, context={'request': request})
            response = {
                'tong_tien': int(total_spent),
                'ap_dung_bao_hiem': int(tong_bao_hiem),
                'thanh_tien': int(thanh_tien),
                'data': serializer.data,
            }
        except ChuoiKham.DoesNotExist:
            response = {
                'tong_tien': '',
                'ap_dung_bao_hiem': '',
                'thanh_tien': '',
                'data': [],
            }
        return Response(response)

class HoaDonLamSangChuoiKham(APIView):
    def get(self, request, format=None):
        id_lich_hen = self.request.query_params.get('id_lich_hen')
        try:
            lich_hen = LichHenKham.objects.get(id=id_lich_hen)
            hoa_don_lam_sang = lich_hen.hoa_don_lam_sang.all()[0]
            serializer = HoaDonLamSangSerializer(hoa_don_lam_sang, context={'request': request})
            response = {
                'data': serializer.data
            }
        except LichHenKham.DoesNotExist:
            response = {
                'data': []
            }
        return Response(response)
        
class HoaDonLamSangGanNhat(APIView):
    def get(self, request, format=None):
        user_id = self.request.query_params.get("user_id")
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_start = now.replace(hour=0, minute=0, second=0)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)
        user = User.objects.get(id=user_id)
        try:
            lich_hen = LichHenKham.objects.filter(benh_nhan=user, thoi_gian_bat_dau__gt=today_start, thoi_gian_bat_dau__lt=today_end).order_by('-thoi_gian_tao').first()
            hoa_don_lam_sang = lich_hen.hoa_don_lam_sang.all()[0]
            serializer = HoaDonLamSangSerializer(hoa_don_lam_sang, context={'request': request})
            response = {
                'data': serializer.data,
            }
        except:
            response = {
                'data': []
            }
        return Response(response)
        
class DanhSachBacSi1(APIView):
    def get(request, self, format=None):
        danh_sach_bac_si = BacSi.objects.all()

        serializer = DanhSachBacSiSerializer(danh_sach_bac_si, many=True, context={'request': request})
        data = serializer.data
       	response = {
            'data': data
        }
        return Response(response)

class DanhSachHoaDonDichVuBaoHiem(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end   = self.request.query_params.get('range_end', None)
 
        start = datetime.strptime(range_start, "%d-%m-%Y")
        tomorrow_start = start + timedelta(1)
        # hoa_don_phan_khoa = []

        if range_end == '':
            hoa_don_dich_vu = HoaDonChuoiKham.objects.filter(Q(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gte=start) | Q(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gte=start)).filter(bao_hiem=True)

        else:
            end = datetime.strptime(range_end, "%d-%m-%Y")
            tomorrow_end = end + timedelta(1)
            hoa_don_dich_vu = HoaDonChuoiKham.objects.filter(bao_hiem=True).filter(Q(thoi_gian_tao__lt=end, thoi_gian_tao__gte=start) | Q(thoi_gian_tao__lt=tomorrow_end, thoi_gian_tao__gte=start))
        

        serializer = HoaDonChuoiKhamSerializer(hoa_don_dich_vu, many=True, context={'request': request})

        response = {
            'data': serializer.data,
        }

        # hoa_don_phan_khoa.clear()
        return Response(response)
        
class DanhSachHoaDonThuocBaoHiem(APIView):
    def get(self, request, format=None):
        range_start = self.request.query_params.get('range_start', None)
        range_end  = self.request.query_params.get('range_end', None)

        start = datetime.strptime(range_start, "%d-%m-%Y")
        tomorrow_start = start + timedelta(1)

        if range_end == '':
            hoa_don_thuoc = HoaDonThuoc.objects.filter(bao_hiem = True).filter(Q(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gte=start) | Q(thoi_gian_tao__lt=tomorrow_start, thoi_gian_tao__gte=start))

        else :
            end = datetime.strptime(range_end, "%d-%m-%Y")
            tomorrow_end = end + timedelta(1)
            hoa_don_thuoc = HoaDonThuoc.objects.filter(bao_hiem = True).filter(Q(thoi_gian_tao__lt=end, thoi_gian_tao__gte=start) | Q(thoi_gian_tao__lt=tomorrow_end, thoi_gian_tao__gte=start))

        serializer = HoaDonThuocSerializer(hoa_don_thuoc, many=True, context = {'request' : request})
        response = {
            'data': serializer.data,
        }

        return Response(response)
class DanhSachBenhNhanChoLamSang(APIView):
    def get(self, request, format=None):
        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Đã Thanh Toán Lâm Sàng")[0] 
        now = timezone.localtime(timezone.now())
        tomorrow = now + timedelta(1)
        today_end = tomorrow.replace(hour=0, minute=0, second=0)

        lich_hen = LichHenKham.objects.filter(trang_thai=trang_thai, thoi_gian_bat_dau__lte=today_end)
        serializer = LichHenKhamSerializer(lich_hen, many=True, context={'request':request})
        response = {
            "error": False,
            "status": status.HTTP_200_OK,
            "message": "Danh Sach Lich Hen Kham",
            "data": serializer.data        
        }
        return Response(response)

# * --- update 6/1/2021 ---

class DanhSachPhongKham(APIView):
    def get(self, request, format=None):
        danh_sach_phong_kham = PhongKham.objects.all()
        serializer = DanhSachPhongKhamSerializer(danh_sach_phong_kham, many=True, context = {'request': request})
        data = serializer.data
        response = {
            'data': data,
        }
        return Response(response)







