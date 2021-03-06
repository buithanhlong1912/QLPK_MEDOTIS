
from finance.models import (
    HoaDonChuoiKham, 
    HoaDonLamSang, 
    HoaDonThuoc, 
    HoaDonTong, 
    HoaDonVatTu
)
from clinic.forms import (
    PhongKhamForm, 
    ThuocForm, 
    UserForm, 
    CongTyForm, 
    DichVuKhamForm, 
    PhongChucNangForm, 
    BacSiForm
)
from medicine.models import (
    DonThuoc, 
    KeDonThuoc, 
    Thuoc, 
    ThuocLog, 
    TrangThaiDonThuoc, 
    VatTu, 
    NhomVatTu,
    KeVatTu,
    CongTy,
    NhomThau,
)
from django.http.response import  JsonResponse
from django.http import HttpResponse
from rest_framework.response import Response
from django.db.models.functions import TruncDay
from django.db.models import Count, F, Sum, Q
from django.db import models
from clinic.models import (
    BacSi, 
    BaiDang, 
    ChuoiKham, 
    DichVuKham, 
    FileKetQua, 
    FileKetQuaChuyenKhoa, 
    FileKetQuaTongQuat, 
    KetQuaChuyenKhoa, 
    KetQuaTongQuat, 
    LichHenKham, 
    LichSuChuoiKham, 
    LichSuTrangThaiKhoaKham, 
    PhanKhoaKham, 
    PhongChucNang, 
    PhongKham, 
    TrangThaiChuoiKham, 
    TrangThaiKhoaKham, 
    TrangThaiLichHen, 
    User
)
from django.shortcuts import render
import json
from django.shortcuts import resolve_url
from django.shortcuts import get_object_or_404
from django.contrib.auth import login as auth_login

from rest_framework.views import APIView
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta
import decimal
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth import authenticate, views as auth_views
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


from datetime import datetime
format = '%m/%d/%Y %H:%M %p'

format_2 = '%d/%m/%Y %H:%M'

format_3 = '%d/%m/%Y'

def getSubName(name):
    lstChar = []
    lstString = name.split(' ')
    for i in lstString:
        lstChar.append(i[0].upper())
    subName = "".join(lstChar)
    return subName


@login_required(login_url='/dang_nhap/')

def index(request):
    nguoi_dung = User.objects.filter(chuc_nang=1)
    # * tổng số bệnh nhân
    ds_bac_si = User.objects.filter(chuc_nang='3')
    # tong_so_benh_nhan = benh_nhan.count()

    # * tổng số hóa đơn
    # tong_so_hoa_don = ChuoiKham.objects.select_related('benh_nhan').all().count()

    # * tổng số đơn thuốc
    # tong_so_don_thuoc = DonThuoc.objects.select_related('benh_nhan').all().count()
    
    # * Danh sách dịch vụ khám
    danh_sach_dich_vu = DichVuKham.objects.all()

    phong_chuc_nang = PhongChucNang.objects.all()
    # * danh sách bệnh nhân chưa được khám
    trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai="Xác Nhận")[0]
    da_dat_truoc = TrangThaiLichHen.objects.get_or_create(ten_trang_thai="Đã đặt trước")[0]
    danh_sach_benh_nhan = LichHenKham.objects.select_related("benh_nhan").filter(trang_thai = trang_thai)
    danh_sach_lich_hen_chua_xac_nhan = LichHenKham.objects.select_related("benh_nhan").filter(trang_thai=da_dat_truoc)

    now = timezone.localtime(timezone.now())
    tomorrow = now + timedelta(1)
    today_start = now.replace(hour=0, minute=0, second=0)
    today_end = tomorrow.replace(hour=0, minute=0, second=0)
    lich_hen = LichHenKham.objects.filter(trang_thai = trang_thai).annotate(relevance=models.Case(
        models.When(thoi_gian_bat_dau__gte=now, then=1),
        models.When(thoi_gian_bat_dau__lt=now, then=2),
        output_field=models.IntegerField(),
    )).annotate(
    timediff=models.Case(
        models.When(thoi_gian_bat_dau__gte=now, then= F('thoi_gian_bat_dau') - now),
        models.When(thoi_gian_bat_dau__lt=now, then=now - F('thoi_gian_bat_dau')),
        # models.When(thoi_gian_bat_dau__lte=today_end - F('thoi_gian_bat_dau')),
        output_field=models.DurationField(),
    )).order_by('relevance', 'timediff')
    
    upcoming_events = []
    past_events = []
    # today_events = LichHenKham.objects.filter(trang_thai = trang_thai, thoi_gian_bat_dau__lte=today_end)
    for lich in lich_hen:
        if lich.relevance == 1:
            upcoming_events.append(lich)
        elif lich.relevance == 2:
            past_events.append(lich)

    now = datetime.now()

    bai_dang = BaiDang.objects.filter(thoi_gian_ket_thuc__gt=now)
    starting_day = datetime.now() - timedelta(days=7)

    user_data = User.objects.filter(thoi_gian_tao__gt=starting_day).annotate(day=TruncDay("thoi_gian_tao")).values("day").annotate(c=Count("id"))
    users = [x["c"] for x in user_data]
    new_users = sum(users)
    labels = [x["day"].strftime("%Y-%m-%d") for x in user_data]

    user_trong_ngay = User.objects.filter(thoi_gian_tao__gte=today_start, thoi_gian_tao__lt=today_end)
    
    hoa_don_chuoi_kham = HoaDonChuoiKham.objects.filter(thoi_gian_tao__gt=starting_day).annotate(day=TruncDay("thoi_gian_tao")).values("day").annotate(c=Count("id")).annotate(total_spent=Sum(F("tong_tien")))
    tong_tien_chuoi_kham = [str(x['total_spent']) for x in hoa_don_chuoi_kham]
    days_chuoi_kham = [x["day"].strftime("%Y-%m-%d") for x in hoa_don_chuoi_kham ]

    hoa_don_thuoc = HoaDonThuoc.objects.filter(thoi_gian_tao__gt=starting_day).annotate(day=TruncDay("thoi_gian_tao")).values("day").annotate(c=Count("id")).annotate(total_spent=Sum(F("tong_tien")))
    tong_tien_thuoc = [str(x['total_spent']) for x in hoa_don_thuoc]
    
    data = {
        'user': request.user,
        # 'tong_so_benh_nhan': tong_so_benh_nhan,
        # 'tong_so_hoa_don': tong_so_hoa_don,
        # 'tong_so_don_thuoc': tong_so_don_thuoc,
        'danh_sach_benh_nhan': danh_sach_benh_nhan,
        'lich_hen_chua_xac_nhan': danh_sach_lich_hen_chua_xac_nhan,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        # 'today_events': today_events,
        'users': users,
        "new_users_count": new_users, 
        'labels': labels,
        'ds_bac_si': ds_bac_si,
        'danh_sach_dich_vu': danh_sach_dich_vu,
        'nguoi_dung': nguoi_dung,
        'user_trong_ngay': user_trong_ngay,
        'tong_tien_chuoi_kham' : tong_tien_chuoi_kham,
        'thoi_gian_chuoi_kham': days_chuoi_kham,
        'tong_tien_thuoc' : tong_tien_thuoc,
        'bai_dang' : bai_dang,
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'index.html', context=data)
    
@login_required(login_url='/dang_nhap/')
def danh_sach_benh_nhan(request):
    danh_sach_benh_nhan = User.objects.filter(chuc_nang = 1)
    trang_thai = TrangThaiLichHen.objects.all()
    phong_chuc_nang = PhongChucNang.objects.all()
    data = {
        'danh_sach_benh_nhan': danh_sach_benh_nhan,
        'trang_thai': trang_thai,
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'le_tan/danh_sach_benh_nhan.html', context=data)

@login_required(login_url='/dang_nhap/')
def update_benh_nhan(request, **kwargs):
    id_benh_nhan = kwargs.get('id')
    instance = get_object_or_404(User, id=id_benh_nhan)
    form = UserForm(request.POST or None, instance=instance)
    phong_chuc_nang = PhongChucNang.objects.all()
    data = {
        'form': form,
        'id_benh_nhan': id_benh_nhan,
        'phong_chuc_nang': phong_chuc_nang,
    }
    return render(request, 'le_tan/update_benh_nhan.html', context=data)

@login_required(login_url='/dang_nhap/')
def cap_nhat_thong_tin_benh_nhan(request):
    if request.method == "POST":
        id_benh_nhan   = request.POST.get('id_benh_nhan')
        ho_ten         = request.POST.get('ho_ten')
        so_dien_thoai  = request.POST.get('so_dien_thoai')
        email          = request.POST.get('email')
        cmnd_cccd      = request.POST.get('cmnd_cccd')
        ngay_sinh      = request.POST.get('ngay_sinh')
        gioi_tinh      = request.POST.get('gioi_tinh')
        dan_toc        = request.POST.get('dan_toc')
        ma_so_bao_hiem = request.POST.get('ma_so_bao_hiem')
        dia_chi        = request.POST.get('dia_chi')

        ngay_sinh = datetime.strptime(ngay_sinh, format_3)
        ngay_sinh = ngay_sinh.strftime("%Y-%m-%d")

        benh_nhan = get_object_or_404(User, id=id_benh_nhan)
        benh_nhan.ho_ten         = ho_ten
        benh_nhan.so_dien_thoai  = so_dien_thoai
        benh_nhan.email          = email
        benh_nhan.cmnd_cccd      = cmnd_cccd
        benh_nhan.dia_chi        = dia_chi
        benh_nhan.ngay_sinh      = ngay_sinh
        benh_nhan.gioi_tinh      = gioi_tinh
        benh_nhan.dan_toc        = dan_toc
        benh_nhan.ma_so_bao_hiem = ma_so_bao_hiem
        benh_nhan.save()

        response = {
            'status': 200,
            'message': 'Cập Nhật Thông Tin Thành Công'
        }
    else:
        response = {
            'status': 404,
            'message': 'Có lỗi xảy ra'
        }
    return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

@login_required(login_url='/dang_nhap/')
class LoginView(auth_views.LoginView):
    template_name = 'registration/login.html'


    def get_success_url(self):
        return resolve_url('trang_chu')

# * Chức năng Lễ Tân
# TODO đăng kí tài khoản cho bệnh nhân tại giao diện dashboard
# TODO xem lịch hẹn khám của bệnh nhân, sau đó xác nhận lại vs bác sĩ và cập nhật lại thời gian cho lịch hẹn khám

@login_required(login_url='/dang_nhap/')
def lich_hen_kham_list(request):
    """ Trả về danh sách lịch hẹn của người dùng mới đặt lịch khám """
    trang_thai = TrangThaiLichHen.objects.get(ten_trang_thai="Đã đặt trước")
    lich_kham = LichHenKham.objects.filter(trang_thai=trang_thai).order_by("-thoi_gian_tao")
    data = {
        'lich_kham': lich_kham
    }
    return render(request, 'index.html', context=data)

def cap_nhat_lich_kham(request, *args, **kwargs):
    # NOTE function này chỉ là dùng khi lễ tân bấm xác nhận, sẽ thay đổi trạng thái của lịch hẹn,
    # NOTE chưa bao gồm thay đổi thời gian của lịch hẹn 
    pk = kwargs.get('pk')
    trang_thai_xac_nhan = TrangThaiLichHen.objects.get_or_create(ten_trang_thai="Xác Nhận")[0]
    lich_hen = get_object_or_404(LichHenKham, pk=pk)
    lich_hen.trang_thai = trang_thai_xac_nhan
    lich_hen.nguoi_phu_trach = request.user
    lich_hen.save()
    return JsonResponse({
        'message': 'Cap Nhat Thanh Cong'
    })

class CapNhatLichKhamAPIToggle(APIView):
    # NOTE: sử dụng toggle này khi kết hợp với ajax, với mục đích là xác nhận lịch hẹn khám
    def get(self, request, format=None, *kwargs):
        pk = kwargs.get('pk')
        obj = get_object_or_404(LichHenKham, pk=pk)
        user_ = self.request.user
        trang_thai_xac_nhan = TrangThaiLichHen.objects.get_or_create(ten_trang_thai="Xác Nhận")[0]
        obj.trang_thai = trang_thai_xac_nhan
        obj.nguoi_phu_trach = user_
        obj.save()
        data = {"message": "Cap Nhat Thanh Cong"}
        return Response(data)
        
# tạo người dùng

# tạo người dùng

def create_user(request):
    if request.user.is_authenticated and request.user.chuc_nang == '2':
        if request.method == "POST":
            ho_ten         = request.POST.get("ho_ten", None)
            so_dien_thoai  = request.POST.get("so_dien_thoai", None)
            password       = request.POST.get("password", None)
            cmnd_cccd      = request.POST.get("cmnd_cccd", None)
            dia_chi        = request.POST.get("dia_chi", None)
            ngay_sinh      = request.POST.get("ngay_sinh", None)
            gioi_tinh      = request.POST.get("gioi_tinh", None)
            dan_toc        = request.POST.get("dan_toc", None)
            ma_so_bao_hiem = request.POST.get("ma_so_bao_hiem", None)

            ngay_sinh = datetime.strptime(ngay_sinh, format_3)
            ngay_sinh = ngay_sinh.strftime("%Y-%m-%d")
            
            if len(ho_ten) == 0:
                return HttpResponse(json.dumps({'message': "Họ Tên Không Được Trống", 'status': '400'}), content_type='application/json; charset=utf-8')

            if User.objects.filter(so_dien_thoai=so_dien_thoai).exists():
                return HttpResponse(json.dumps({'message': "Số Điện Thoại Đã Tồn Tại", 'status': '409'}), content_type='application/json; charset=utf-8')

            if User.objects.filter(cmnd_cccd=cmnd_cccd).exists():
                return HttpResponse(json.dumps({'message': "Số chứng minh thư đã tồn tại", 'status': '403'}), content_type = 'application/json; charset=utf-8')

            user = User.objects.create_nguoi_dung(
                ho_ten         = ho_ten, 
                so_dien_thoai  = so_dien_thoai, 
                password       = password,
                cmnd_cccd      = cmnd_cccd,
                dia_chi        = dia_chi,
                ngay_sinh      = ngay_sinh,
                gioi_tinh      = gioi_tinh,
                dan_toc        = dan_toc,    
                ma_so_bao_hiem = ma_so_bao_hiem,
            )
            user.save()

            response = {
                "message": "Đăng Kí Người Dùng Thành Công",
                "ho_ten": user.ho_ten,
                "so_dien_thoai": user.so_dien_thoai,
            }

            return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
        else:
            return HttpResponse(
                json.dumps({"nothing to see": "this isn't happening"}),
                content_type="application/json"
            )
    else:
        response = {
            'status': 404,
            'message': "Bạn Không Có Quyền Thêm Người Dùng"
        }
        return HttpResponse(
            json.dumps(response),
            content_type="application/json", charset="utf-8"
        )

def add_lich_hen(request):      
    if request.method == "POST":
        id_benh_nhan      = request.POST.get('id_benh_nhan')
        thoi_gian_bat_dau = request.POST.get('thoi_gian_bat_dau')
        ly_do             = request.POST.get('ly_do')
        loai_dich_vu      = request.POST.get('loai_dich_vu')
        user              = User.objects.get(id=id_benh_nhan)

        thoi_gian_bat_dau = datetime.strptime(thoi_gian_bat_dau, format_2)
        thoi_gian = thoi_gian_bat_dau.strftime("%Y-%m-%d %H:%M")

        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Chờ Thanh Toán Lâm Sàng")[0]
        lich_hen = LichHenKham.objects.create(
            benh_nhan         = user,
            nguoi_phu_trach   = request.user,
            thoi_gian_bat_dau = thoi_gian,
            ly_do             = ly_do,
            loai_dich_vu      = loai_dich_vu,
            trang_thai        = trang_thai, 
        )
        lich_hen.save()

        response = {
            'message': "Bệnh nhân " + user.ho_ten
        }
    else: 
        response = {
            'message': "Có lỗi xảy ra"
        }
    return HttpResponse(json.dumps(response), content_type='application/json; charset=utf-8')

def create_thuoc(request):
    if request.method == "POST":
        id_cong_ty        = request.POST.get('id_cong_ty')
        ma_hoat_chat      = request.POST.get('ma_hoat_chat')
        ten_hoat_chat     = request.POST.get('ten_hoat_chat')
        ham_luong         = request.POST.get('ham_luong')
        duong_dung        = request.POST.get('duong_dung')
        ma_thuoc          = request.POST.get("ma_thuoc")
        ten_thuoc         = request.POST.get("ten_thuoc")
        so_dang_ky        = request.POST.get('so_dang_ky')
        dong_goi          = request.POST.get('dong_goi')
        don_vi_tinh       = request.POST.get('don_vi_tinh')
        don_gia           = request.POST.get("don_gia")
        don_gia_tt        = request.POST.get("don_gia_tt")
        so_lo             = request.POST.get('so_lo')
        so_luong_kha_dung = request.POST.get("so_luong_kha_dung")
        hang_sx           = request.POST.get("hang_san_xuat")
        nuoc_sx           = request.POST.get("nuoc_san_xuat")
        quyet_dinh        = request.POST.get("quyet_dinh")
        cong_bo           = request.POST.get("cong_bo")
        loai_thuoc        = request.POST.get("loai_thuoc")
        han_su_dung       = request.POST.get("han_su_dung")
        ngay_san_xuat     = request.POST.get("ngay_san_xuat")

        han_su_dung = datetime.strptime(han_su_dung, format_3)
        han_su_dung = han_su_dung.strftime("%Y-%m-%d")

        ngay_san_xuat = datetime.strptime(ngay_san_xuat, format_3)
        ngay_san_xuat = ngay_san_xuat.strftime("%Y-%m-%d")        
    
        cong_ty = CongTy.objects.get(id=id_cong_ty)

        Thuoc.objects.create(
            cong_ty           = cong_ty,
            ma_hoat_chat      = ma_hoat_chat,
            ten_hoat_chat     = ten_hoat_chat,
            ham_luong         = ham_luong,
            duong_dung        = duong_dung,
            ma_thuoc          = ma_thuoc,
            ten_thuoc         = ten_thuoc,
            so_dang_ky        = so_dang_ky,
            dong_goi          = dong_goi,
            don_vi_tinh       = don_vi_tinh,
            don_gia           = don_gia,
            don_gia_tt        = don_gia_tt,
            so_lo             = so_lo,
            so_luong_kha_dung = so_luong_kha_dung,
            hang_sx           = hang_sx,
            nuoc_sx           = nuoc_sx,
            quyet_dinh        = quyet_dinh,
            cong_bo           = cong_bo,
            loai_thuoc        = loai_thuoc,
            han_su_dung       = han_su_dung,
            ngay_san_xuat     = ngay_san_xuat
        )

        response = {
            'status' : 200,
            'message' : 'Tạo Thành Công'
        }
    else:
        response = {
            'status': 404,
            'message': "Có Lỗi Xảy Ra"
        }    
    return HttpResponse(json.dumps(response), content_type='application/json; charset=utf-8')
        
    # return HttpResponse('upload')
# * function này không cần dùng tới template

def create_dich_vu(request):
    if request.method == "POST":
        ma_dvkt          = request.POST.get("ma_dvkt")
        ten_dvkt         = request.POST.get("ten_dvkt")
        don_gia          = request.POST.get("don_gia")
        ma_gia           = request.POST.get("ma_gia")
        quyet_dinh       = request.POST.get("quyet_dinh")
        cong_bo          = request.POST.get("cong_bo")
        phong_chuc_nang  = request.POST.get("phong_chuc_nang")

        phong_chuc_nang = PhongChucNang.objects.get(id=phong_chuc_nang)

        DichVuKham.objects.create(
            ma_dvkt          = ma_dvkt, 
            ten_dvkt         = ten_dvkt, 
            don_gia          = don_gia, 
            ma_gia           = ma_gia, 
            quyet_dinh       = quyet_dinh, 
            cong_bo          = cong_bo, 
            phong_chuc_nang  = phong_chuc_nang,  
        )

        response = {
            'status' : 200,
            'message' : 'Tạo Thành Công',
        }
    else:
        response = {
            'status' : 404,
            'message' : 'Có Lỗi Xảy Ra',
        }    
    return HttpResponse(json.dumps(response), content_type='application/json; charset=utf-8')


class BatDauChuoiKhamAPIToggle(APIView):
    """ 
    * Khi bác sĩ lâm sàng bấm bắt đầu khám cho một bệnh nhân nào đó, thì chuỗi khám sẽ tự động được tạo
    """
    def get(self, request, format=None, **kwargs):
        user_id = kwargs.get('id')
        user = get_object_or_404(User, id=user_id)
        bac_si_lam_sang = self.request.user
        now = timezone.localtime(timezone.now())
        trang_thai = TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham="Đang thực hiện")[0]
        chuoi_kham = ChuoiKham.objects.create(
            benh_nhan = user,
            bac_si_dam_nhan = bac_si_lam_sang,
            thoi_gian_bat_dau = now,
            trang_thai = trang_thai
        )
        chuoi_kham.save()
        messages.success(request, 'Bắt đầu chuỗi khám')
        data = {
            "message": "Chuỗi Khám Bắt Đầu"
        }
        return Response(data)

class KetThucChuoiKhamAPI(APIView):
    """ 
    * Khi bác sĩ lâm sàng bấm kết thúc chuỗi khám thì chuỗi khám của người dùng sẽ được cập nhật thêm thời gian kết thúc và sẽ chuyển trạng thái sang Hoàn thành
    """

    def get(self, request, format=None, **kwargs):
        chuoi_kham_id = kwargs.get('id', None)
        if chuoi_kham_id == None:
            messages.error(request, 'Không thể kết thúc chuỗi khám')
            messages.debug(request, f'Chuỗi khám không tồn tại (id:{chuoi_kham_id})')
            return Response({
                "message": "Khong The Ket Thuc Chuoi Kham Vi Chua Bat Dau Chuoi Kham"
            })
        else:
            trang_thai = TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham="Hoàn Thành")[0]
            chuoi_kham = get_object_or_404(ChuoiKham, pk = chuoi_kham_id)
            chuoi_kham.thoi_gian_ket_thuc = timezone.localtime(timezone.now())
            chuoi_kham.trang_thai = trang_thai
            chuoi_kham.save()
            messages.success(request, 'Kết thúc chuỗi khám')
        data = {
            "message": "Ket Thuc Chuoi Kham"
        }
        return Response(data)

    # * Đoạn này dùng để sắp xếp lịch hẹn theo trình từ upcoming-past
    # * upcoming events: ascendant order
    # * past events: descendant order
    #     LichHenKham.objects.annotate(relevance=models.Case(
    #     models.When(thoi_gian_bat_dau__gte=now, then=1),
    #     models.When(thoi_gian_bat_dau__lt=now, then=2),
    #     output_field=models.IntegerField(),
    # )).annotate(
    # timediff=models.Case(
    #     models.When(thoi_gian_bat_dau__gte=now, then=F('thoi_gian_bat_dau') - now),
    #     models.When(thoi_gian_bat_dau__lt=now, then=now - F('thoi_gian_bat_dau')),
    #     output_field=models.DurationField(),
    # )).order_by('relevance', 'timediff')

# TODO hiển thị danh sách bệnh nhân chờ khám đối với từng phòng chức năng
@login_required(login_url='/dang_nhap/')
def danh_sach_benh_nhan_cho(request):
    trang_thai = TrangThaiLichHen.objects.all()
    trang_thai_ck = TrangThaiChuoiKham.objects.all()
    phong_chuc_nang = PhongChucNang.objects.all()

    return render(request, 'bac_si_lam_sang/danh_sach_benh_nhan_cho.html', context={"trang_thai": trang_thai, "trang_thai_ck": trang_thai_ck, "phong_chuc_nang": phong_chuc_nang})

@login_required(login_url='/dang_nhap/')
def phong_chuyen_khoa(request, *args, **kwargs):
    # phong_chuc_nang = PhongChucNang.objects.values('ten_phong_chuc_nang').distinct()
    phong_chuc_nang = PhongChucNang.objects.all()
    id_phong_chuc_nang = kwargs.get('id_phong_chuc_nang', None)
    phong_chuc_nang_detail = PhongChucNang.objects.get(id=id_phong_chuc_nang)

    trang_thai = TrangThaiChuoiKham.objects.all()
    data = {
        'phong_chuc_nang': phong_chuc_nang,
        'trang_thai': trang_thai,
        'id_phong_chuc_nang' : id_phong_chuc_nang,
        'phong_chuc_nang_detail': phong_chuc_nang_detail
    }
    return render(request, 'bac_si_chuyen_khoa/phong_chuyen_khoa.html', context=data)

@login_required(login_url='/dang_nhap/')
def phan_khoa_kham(request, **kwargs):
    id_lich_hen = kwargs.get('id_lich_hen', None)
    lich_hen    = LichHenKham.objects.get(id = id_lich_hen)
    phong_chuc_nang = PhongChucNang.objects.all()

    data = {
        'id_lich_hen': id_lich_hen,
        'lich_hen'   : lich_hen,
        'phong_chuc_nang' : phong_chuc_nang,

    }
    return render(request, 'bac_si_lam_sang/phan_khoa_kham.html', context=data)

def store_phan_khoa(request):
    if request.method == "POST":
        request_data = request.POST.get('data', None)
        user         = request.POST.get('user', None)
        id_lich_hen  = request.POST.get('id_lich_hen', None)
        data         = json.loads(request_data)

        now       = datetime.now()
        date_time = now.strftime("%m%d%y%H%M%S")

        bulk_create_data = []
        user = User.objects.get(id = user)
        subName = getSubName(user.ho_ten)
        ma_hoa_don = "HD" + "-" + subName + '-' + date_time

        lich_hen = LichHenKham.objects.get(id = id_lich_hen)
        trang_thai_lich_hen = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Đã Phân Khoa")[0]
        lich_hen.trang_thai = trang_thai_lich_hen
        lich_hen.save()
        trang_thai = TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham="Chờ Thanh Toán")[0]
        chuoi_kham = ChuoiKham.objects.get_or_create(bac_si_dam_nhan=request.user, benh_nhan=user, trang_thai=trang_thai, lich_hen = lich_hen)[0]
        chuoi_kham.save()
        hoa_don = HoaDonChuoiKham.objects.create(chuoi_kham=chuoi_kham, ma_hoa_don=ma_hoa_don)
        hoa_don.save()

        for i in data:
            index = data.index(i)
            priority = index + 1
            dich_vu = DichVuKham.objects.only('id').get(id=i['obj']['id'])
            bac_si = request.user
            bulk_create_data.append(PhanKhoaKham(benh_nhan=user, dich_vu_kham=dich_vu, bao_hiem=i['obj']['bao_hiem'], bac_si_lam_sang=bac_si, chuoi_kham=chuoi_kham, priority=priority))

        PhanKhoaKham.objects.bulk_create(bulk_create_data)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}", {
                'type':'checkup_process_info'
            }
        )
        async_to_sync(channel_layer.group_send)(
            f"checkup_process_user_{lich_hen.benh_nhan.id}", {
                'type':'checkup_process_notification'
            }
        )

        response = {
            'status' : 200,
            'message': "Phân Khoa Khám Thành Công!",
            'url' : '/bac_si_lam_sang/danh_sach_benh_nhan_cho/'
        }

        return HttpResponse(json.dumps(response), content_type='application/json; charset=utf-8')

def store_ke_don(request):
    if request.method == "POST":
        request_data = request.POST.get('data', None)
        user = request.POST.get('user', None)
        id_chuoi_kham = request.POST.get('id_chuoi_kham', None)
        data = json.loads(request_data)

        now = datetime.now()
        date_time = now.strftime("%m%d%y%H%M%S")
        
        chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
        
        bulk_create_data = []
        user = User.objects.get(id=user)
        subName = getSubName(user.ho_ten)
        ma_don_thuoc = subName + '-' + date_time
        trang_thai = TrangThaiDonThuoc.objects.get_or_create(trang_thai="Chờ Thanh Toán")[0]
        don_thuoc = DonThuoc.objects.get_or_create(benh_nhan=user, bac_si_ke_don=request.user, trang_thai=trang_thai, ma_don_thuoc=ma_don_thuoc, chuoi_kham = chuoi_kham)[0]
        trang_thai_lich_hen = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Chờ Thanh Toán Hóa Đơn Thuốc")[0]
        # lich_hen = 
        don_thuoc.save()

        for i in data:
            thuoc = Thuoc.objects.only('id').get(id=i['obj']['id'])
            ke_don_thuoc = KeDonThuoc(don_thuoc=don_thuoc, thuoc=thuoc, so_luong=i['obj']['so_luong'], cach_dung=i['obj']['duong_dung'], ghi_chu=i['obj']['ghi_chu'], bao_hiem=i['obj']['bao_hiem'])
            bulk_create_data.append(ke_don_thuoc)

        KeDonThuoc.objects.bulk_create(bulk_create_data)
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"prescription_user_{user.id}", {
                'type':'prescription_notification'
            }
        )
        response = {'status': 200, 'message': 'Kê Đơn Thành Công', 'url': '/danh_sach_kham/'}
    else:
       response = {'message': 'oke'} 
    return HttpResponse(json.dumps(response), content_type='application/json; charset=utf-8')

def chinh_sua_don_thuoc(request):
    if request.method == "POST":
        request_data = request.POST.get('data')
        ma_don_thuoc = request.POST.get('ma_don_thuoc')
        data = json.loads(request_data)
        new_dict = {}
        # print(data[0])
        # print(ma_don_thuoc)
        so_luong = data[0]
        ghi_chu = data[1]
        # print(data)
        don_thuoc = DonThuoc.objects.get(ma_don_thuoc=ma_don_thuoc)
        for k in so_luong.keys():
            new_dict[k] = tuple(new_dict[k] for new_dict in data)
        
        print(new_dict)
        for k in new_dict.keys():
            id_thuoc = k
            so_luong_thuoc = new_dict[k][0]
            ghi_chu_thuoc = new_dict[k][1]
            id_ke_don = new_dict[k][2]
            ke_don = KeDonThuoc.objects.get(id=id_ke_don)
            ke_don.so_luong = so_luong_thuoc
            ke_don.ghi_chu = ghi_chu_thuoc
            ke_don.save()
            
        response = {'status': 200, 'message': 'Cập Nhật Thành Công'}
        return HttpResponse(json.dumps(response), content_type='application/json; charset=utf-8')

def files_upload_view(request):
    print(request.FILES)
    if request.method == "POST":
        ma_ket_qua = request.POST.get('ma_ket_qua', None)
        mo_ta = request.POST.get('mo_ta', None)
        ket_luan = request.POST.get('ket_qua', None)
        id_chuoi_kham = request.POST.get('id_chuoi_kham')
        print(id_chuoi_kham)

        if ma_ket_qua == '':
            HttpResponse({'status': 404, 'message': 'Mã Kết Quả Không Được Để Trống'})

        if mo_ta == '':
            HttpResponse({'status': 404, 'message': 'Mô Tả Không Được Để Trống'})

        if ket_luan == '':
            HttpResponse({'status': 404, 'message': 'Kết Luận Không Được Để Trống'})

        # chuoi_kham = ChuoiKham.objects.get(id=16)
        # ket_qua_tong_quat = KetQuaTongQuat.objects.get_or_create(chuoi_kham=chuoi_kham, ma_ket_qua=ma_ket_qua, mo_ta=mo_ta, ket_luan=ket_luan)[0]
        
        # for value in request.FILES.values():
        #     file = FileKetQua.objects.create(file=value)
        #     file_kq_tong_quat = FileKetQuaTongQuat.objects.create(ket_qua_tong_quat=ket_qua_tong_quat, file=file)
        #     file_kq_tong_quat.save()

        return HttpResponse('upload')
    return JsonResponse({'post': False})

def upload_files_chuyen_khoa(request):

    if request.method == "POST":
        ma_ket_qua    = request.POST.get('ma_ket_qua', None)
        mo_ta         = request.POST.get('mo_ta', None)
        ket_luan      = request.POST.get('ket_qua', None)
        id_chuoi_kham = request.POST.get('id_chuoi_kham')

        if ma_ket_qua == '':
            HttpResponse({'status': 404, 'message': 'Mã Kết Quả Không Được Để Trống'})

        if mo_ta == '':
            HttpResponse({'status': 404, 'message': 'Mô Tả Không Được Để Trống'})

        if ket_luan == '':
            HttpResponse({'status': 404, 'message': 'Kết Luận Không Được Để Trống'})

        chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
        ket_qua_tong_quat = KetQuaTongQuat.objects.get_or_create(chuoi_kham=chuoi_kham)[0]
        ket_qua_chuyen_khoa = KetQuaChuyenKhoa.objects.create(ket_qua_tong_quat=ket_qua_tong_quat, ma_ket_qua=ma_ket_qua, mo_ta=mo_ta, ket_luan=ket_luan)

        for value in request.FILES.values():
            
            # fs = FileSystemStorage() 
            # file = fs.save(value.name, value) 
            # # the fileurl variable now contains the url to the file. This can be used to serve the file when needed. 
            # fs.url(file)
            file = FileKetQua.objects.create(file=value)
            file_kq_chuyen_khoa = FileKetQuaChuyenKhoa.objects.create(ket_qua_chuyen_khoa=ket_qua_chuyen_khoa, file=file)
        
        return HttpResponse('upload')
    response = {
        'status': 200,
        'message' : 'Upload Thành Công!'
    }
    return HttpResponse(json.dumps(response), content_type='application/json; charset=utf-8')

def upload_files_lam_sang(request):
    print(request.FILES)
    if request.method == "POST":
        ma_ket_qua = request.POST.get('ma_ket_qua', None)
        mo_ta = request.POST.get('mo_ta', None)
        ket_luan = request.POST.get('ket_qua', None)
        id_chuoi_kham = request.POST.get('id_chuoi_kham')

        if ma_ket_qua == '':
            HttpResponse({'status': 404, 'message': 'Mã Kết Quả Không Được Để Trống'})

        if mo_ta == '':
            HttpResponse({'status': 404, 'message': 'Mô Tả Không Được Để Trống'})

        if ket_luan == '':
            HttpResponse({'status': 404, 'message': 'Kết Luận Không Được Để Trống'})

        chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
        ket_qua_tong_quat = KetQuaTongQuat.objects.get_or_create(chuoi_kham=chuoi_kham)[0]
        ket_qua_tong_quat.ma_ket_qua = ma_ket_qua
        ket_qua_tong_quat.mo_ta = mo_ta
        ket_qua_tong_quat.ket_luan = ket_luan
        ket_qua_tong_quat.save()

        for value in request.FILES.values():
            file = FileKetQua.objects.create(file=value)
            file_ket_qua_tong_quat = FileKetQuaTongQuat.objects.create(file=file, ket_qua_tong_quat=ket_qua_tong_quat)

        return HttpResponse('upload')
    return JsonResponse({'post': False})

@login_required(login_url='/dang_nhap/')
def upload_view(request, **kwargs):
    id_chuoi_kham = kwargs.get('id')
    chuoi_kham = ChuoiKham.objects.get(id = id_chuoi_kham)
    id_phong_chuc_nang = kwargs.get('id_phong_chuc_nang')
    phong_chuc_nang = PhongChucNang.objects.all()
    ten_phong_chuc_nang = PhongChucNang.objects.get(id = id_phong_chuc_nang)
    ho_ten_benh_nhân = chuoi_kham.benh_nhan.ho_ten
    ten_phong_chuc_nang = ten_phong_chuc_nang.ten_phong_chuc_nang
    now       = datetime.now()
    date_time = now.strftime("%m%d%y%H%M%S")

    ma_ket_qua = str(id_phong_chuc_nang) +'-'+ getSubName(ho_ten_benh_nhân) + '-' + str(date_time)
    data = {
        'id_chuoi_kham' : id_chuoi_kham,
        'chuoi_kham' : chuoi_kham,
        'phong_chuc_nang' : phong_chuc_nang,
        'id_phong_chuc_nang' : id_phong_chuc_nang,
        'ma_ket_qua': ma_ket_qua,
    }
    return render(request, 'bac_si_chuyen_khoa/upload.html', context=data)

@login_required(login_url='/dang_nhap/')
def upload_view_lam_sang(request, **kwargs):
    id_chuoi_kham = kwargs.get('id')
    chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
    ho_ten_benh_nhan = chuoi_kham.benh_nhan.ho_ten
    now = datetime.now()
    date_time = now.strftime("%m%d%y%H%M%S")
 
    ma_ket_qua = getSubName(ho_ten_benh_nhan) +'-'+ str(date_time)
    phong_chuc_nang = PhongChucNang.objects.all()
 
    data = {
        'id_chuoi_kham' : id_chuoi_kham,
        'phong_chuc_nang' : phong_chuc_nang,
        'ma_ket_qua' : ma_ket_qua,
    }
    return render(request, 'bac_si_lam_sang/upload_ket_qua.html', context=data)

@login_required(login_url='/dang_nhap/')
def phong_tai_chinh_danh_sach_cho(request):
    trang_thai = TrangThaiChuoiKham.objects.all()
    phong_chuc_nang = PhongChucNang.objects.all()

    data = {
        'trang_thai' : trang_thai,
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'phong_tai_chinh/danh_sach_thanh_toan.html', context= data)

@login_required(login_url='/dang_nhap/')
def phong_thuoc_danh_sach_cho(request):
    phong_chuc_nang = PhongChucNang.objects.all()

    data = {
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'phong_thuoc/danh_sach_cho.html', context=data)

@login_required(login_url='/dang_nhap/')
def hoa_don_dich_vu(request, **kwargs):
    id_chuoi_kham = kwargs.get('id_chuoi_kham')
    # chuoi_kham = ChuoiKham.objects.filter(benh_nhan__id=user_id, trang_thai__id = 4)[0]
    chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
    hoa_don_dich_vu = chuoi_kham.hoa_don_dich_vu
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
    phong_chuc_nang = PhongChucNang.objects.all()
    
    data = {
        'chuoi_kham'         : chuoi_kham,
        'tong_tien'          : total_spent,
        'phong_chuc_nang'    : phong_chuc_nang,
        'danh_sach_phan_khoa': danh_sach_phan_khoa,
        'tong_tien'          : total_spent,
        'ap_dung_bao_hiem'   : tong_bao_hiem,
        'thanh_tien'         : thanh_tien,
        'hoa_don_dich_vu'    : hoa_don_dich_vu
    }
    return render(request, 'phong_tai_chinh/hoa_don_dich_vu.html', context=data)

@login_required(login_url='/dang_nhap/')
def hoa_don_thuoc(request, **kwargs):
    id_don_thuoc = kwargs.get('id_don_thuoc')
    don_thuoc = DonThuoc.objects.get(id = id_don_thuoc)
    danh_sach_thuoc = don_thuoc.ke_don.all()
    # tong_tien = []
    # for thuoc_instance in danh_sach_thuoc:
    #     gia = int(thuoc_instance.thuoc.don_gia_tt) * thuoc_instance.so_luong
    #     tong_tien.append(gia)
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
    
    total_spent = sum(tong_tien)
    tong_tien.clear()
    bao_hiem.clear()
    
    phong_chuc_nang = PhongChucNang.objects.all()

    data = {
        'danh_sach_thuoc': danh_sach_thuoc,
        'tong_tien'      : total_spent,
        'don_thuoc'      : don_thuoc,
        'phong_chuc_nang': phong_chuc_nang,
        'thanh_tien'     : thanh_tien,
        'tong_bao_hiem'  : tong_bao_hiem,
    }
    return render(request, 'phong_tai_chinh/hoa_don_thuoc.html', context=data)

@login_required(login_url='/dang_nhap/')
def don_thuoc(request, **kwargs):
    id_don_thuoc = kwargs.get('id_don_thuoc')
    don_thuoc = DonThuoc.objects.get(id = id_don_thuoc)
    danh_sach_thuoc = don_thuoc.ke_don.all()
    phong_chuc_nang = PhongChucNang.objects.all()

    data = {
        'danh_sach_thuoc': danh_sach_thuoc,
        'don_thuoc' : don_thuoc,
        'id_don_thuoc': id_don_thuoc,
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'phong_thuoc/don_thuoc.html', context=data)

@login_required(login_url='/dang_nhap/')
def danh_sach_kham(request):
    trang_thai = TrangThaiLichHen.objects.all()
    trang_thai_ck = TrangThaiChuoiKham.objects.all()
    phong_chuc_nang = PhongChucNang.objects.all()

    return render(request, 'bac_si_lam_sang/danh_sach_kham.html', context={"trang_thai": trang_thai, "trang_thai_ck": trang_thai_ck, 'phong_chuc_nang' : phong_chuc_nang})


def login(request):
    return render(request, 'registration/login.html')

class BatDauChuoiKhamToggle(APIView):
    def get(self, request, format=None, **kwargs):
        id_phan_khoa = request.GET.get('id', None)
        print(id_phan_khoa)
        phan_khoa_kham = PhanKhoaKham.objects.get(id=id_phan_khoa)
        chuoi_kham = phan_khoa_kham.chuoi_kham
        trang_thai_chuoi_kham = TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham="Đang Thực Hiện")[0]
        trang_thai_phan_khoa = TrangThaiKhoaKham.objects.get_or_create(trang_thai_khoa_kham="Đang Thực Hiện")[0]

        now = timezone.localtime(timezone.now())
        if phan_khoa_kham.priority == 1:
            chuoi_kham.thoi_gian_bat_dau = now
            chuoi_kham.trang_thai = trang_thai_chuoi_kham
            phan_khoa_kham.thoi_gian_bat_dau = now
            phan_khoa_kham.trang_thai = trang_thai_phan_khoa
            chuoi_kham.save()
            phan_khoa_kham.save()
            dich_vu = phan_khoa_kham.dich_vu_kham.ten_dvkt
            response = {'status': '200', 'message': f'Bắt Đầu Chuỗi Khám, Dịch Vụ Khám Đầu Tiên: {dich_vu}', 'time': f'{now}'}
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{phan_khoa_kham.benh_nhan.id}", {
                    'type':'checkup_process_info'
                }
            )
            async_to_sync(channel_layer.group_send)(
                f"funcroom_service", {
                    'type': 'funcroom_info'
                }
            )
            
            return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
        else:
            phan_khoa_kham.thoi_gian_bat_dau = now
            chuoi_kham.trang_thai = trang_thai_chuoi_kham
            phan_khoa_kham.trang_thai = trang_thai_phan_khoa
            chuoi_kham.save()
            phan_khoa_kham.save()
            dich_vu = phan_khoa_kham.dich_vu_kham.ten_dvkt
            response = {'status': '200', 'message': f'Bắt Đầu Dịch Vụ: {dich_vu}', 'time': f'{now}'}
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{phan_khoa_kham.benh_nhan.id}", {
                    'type':'checkup_process_info'
                }
            )
            async_to_sync(channel_layer.group_send)(
                f"funcroom_service", {
                    'type': 'funcroom_info'
                }
            )
            
            return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
 
class KetThucChuoiKhamToggle(APIView):
    def get(self, request, format=None, **kwargs):
        id_phan_khoa = request.GET.get('id', None)
        print(id_phan_khoa)
        phan_khoa_kham = PhanKhoaKham.objects.get(id=id_phan_khoa)
        chuoi_kham = phan_khoa_kham.chuoi_kham
        trang_thai_chuoi_kham = TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham="Đang Thực Hiện")[0]
        trang_thai_phan_khoa = TrangThaiKhoaKham.objects.get_or_create(trang_thai_khoa_kham="Hoàn Thành")[0]
        priotity = chuoi_kham.phan_khoa_kham.all().aggregate(Max('priority'))
        now = timezone.localtime(timezone.now())
        print(priotity['priority__max'])
        if phan_khoa_kham.priority == priotity['priority__max']:
            chuoi_kham.thoi_gian_ket_thuc = now
            phan_khoa_kham.thoi_gian_ket_thuc = now
            chuoi_kham.trang_thai = trang_thai_chuoi_kham
            phan_khoa_kham.trang_thai = trang_thai_phan_khoa
            chuoi_kham.save()
            phan_khoa_kham.save()
            dich_vu = phan_khoa_kham.dich_vu_kham.ten_dvkt
            response = {'status': '200', 'message': f'Kết Thúc Chuỗi Khám, Dịch Vụ Khám Cuối Cùng: {dich_vu}', 'time': f'{now}'}
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{phan_khoa_kham.benh_nhan.id}", {
                    'type':'checkup_process_info'
                }
            )
            async_to_sync(channel_layer.group_send)(
                f"funcroom_service", {
                    'type': 'funcroom_info'
                }
            )

            return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
        else:
            phan_khoa_kham.thoi_gian_ket_thuc = now
            phan_khoa_kham.trang_thai = trang_thai_phan_khoa
            phan_khoa_kham.save()
            dich_vu = phan_khoa_kham.dich_vu_kham.ten_dvkt
            response = {'status': '200', 'message': f'Kết Thúc Dịch Vụ: {dich_vu}', 'time': f'{now}'}
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{phan_khoa_kham.benh_nhan.id}", {
                    'type':'checkup_process_info'
                }
            )
            async_to_sync(channel_layer.group_send)(
                f"funcroom_service", {
                    'type': 'funcroom_info'
                }
            )

            return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

def bat_dau_chuoi_kham(request, **kwargs):
    id_phan_khoa = kwargs.get('id', None)
    phan_khoa_kham = PhanKhoaKham.objects.get(id=id_phan_khoa)
    chuoi_kham = phan_khoa_kham.chuoi_kham
    now = timezone.localtime(timezone.now())
    if phan_khoa_kham.priority == 1:
        chuoi_kham.thoi_gian_bat_dau = now
        phan_khoa_kham.thoi_gian_bat_dau = now
        chuoi_kham.save()
        phan_khoa_kham.save()
        dich_vu = phan_khoa_kham.dich_vu_kham.ten_dvkt
        response = {'status': '200', 'message': f'Bắt Đầu Chuỗi Khám, Dịch Vụ Khám: {dich_vu}', 'time': f'{now}'}
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
    else:
        phan_khoa_kham.thoi_gian_bat_dau = now
        phan_khoa_kham.save()
        dich_vu = phan_khoa_kham.dich_vu_kham.ten_dvkt
        response = {'status': '200', 'message': f'Bắt Đầu Dịch Vụ: {dich_vu}', 'time': f'{now}'}
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

@login_required(login_url='/dang_nhap/')
def danh_sach_thuoc(request):
    phong_chuc_nang = PhongChucNang.objects.all()

    data = {
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'phong_thuoc/danh_sach_thuoc.html', context=data)

@login_required(login_url='/dang_nhap/')
def danh_sach_thuoc_phong_tai_chinh(request):
    nhom_thau = NhomThau.objects.all()
    phong_chuc_nang = PhongChucNang.objects.all()

    data={
        'nhom_thau': nhom_thau,
        'phong_chuc_nang': phong_chuc_nang,
    }
    return render(request, 'phong_tai_chinh/danh_sach_thuoc.html', context = data)

@login_required(login_url='/dang_nhap/')
def them_moi_thuoc_phong_tai_chinh(request):
    phong_chuc_nang = PhongChucNang.objects.all()
    cong_ty = CongTy.objects.all()
    data = {
        'cong_ty': cong_ty,
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'phong_tai_chinh/them_moi_thuoc.html', context=data)

@login_required(login_url='/dang_nhap/')
def cong_ty(request):
    phong_chuc_nang = PhongChucNang.objects.all()

    data = {
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'phong_tai_chinh/nguon_cung.html', context=data)

@login_required(login_url='/dang_nhap/')
def update_lich_hen(request, **kwargs):
    id_lich_hen = kwargs.get('id')
    phong_chuc_nang = PhongChucNang.objects.all()
    lich_hen_kham = LichHenKham.objects.get(id=id_lich_hen)
    data = {
        'lich_hen' : lich_hen_kham,
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'le_tan/update_lich_hen.html', context=data)

@login_required(login_url='/dang_nhap/')
def danh_sach_lich_hen(request):
    trang_thai = TrangThaiLichHen.objects.all()
    phong_chuc_nang = PhongChucNang.objects.all()
    nguoi_dung = User.objects.filter(chuc_nang=1)
    data = {
        'trang_thai' : trang_thai,
        'nguoi_dung' : nguoi_dung,
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'le_tan/danh_sach_lich_hen.html', context=data)

def store_update_lich_hen(request):
    if request.method == 'POST':
        thoi_gian_bat_dau = request.POST.get('thoi_gian_bat_dau')
        id_lich_hen = request.POST.get('id')
        thoi_gian_bat_dau = datetime.strptime(thoi_gian_bat_dau, format_2)
        thoi_gian = thoi_gian_bat_dau.strftime("%Y-%m-%d %H:%M")
        trang_thai = TrangThaiLichHen.objects.get(ten_trang_thai = "Xác Nhận")
        lich_hen = LichHenKham.objects.get(id=id_lich_hen)
        lich_hen.thoi_gian_bat_dau = thoi_gian
        lich_hen.trang_thai = trang_thai
        lich_hen.save()
        response = {
            "message" : "Cập Nhật Thành Công"
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

@login_required(login_url='/dang_nhap/')   
def them_thuoc_phong_tai_chinh(request):
    cong_ty = CongTy.objects.all()
    phong_chuc_nang = PhongChucNang.objects.all()
    
    data = {
        'cong_ty' : cong_ty,
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'phong_tai_chinh/them_moi_thuoc.html', context=data)

@transaction.atomic
def xuat(request, id=None, so_luong=None):
    try:
        thuoc = Thuoc.objects.filter(id=id)
        print(thuoc[0].kha_dung, end="\n\n\n")
        if thuoc[0].kha_dung:
            thuoc.update(so_luong_kha_dung=F('so_luong_kha_dung') - so_luong)
            ThuocLog.objects.create(thuoc=thuoc[0], ngay=timezone.now(), quy_trinh=ThuocLog.OUT, so_luong=so_luong)
        else:
            return Response({"error": True, "message": "So Luong Thuoc Kha Dung = 0, Khong The Xuat Thuoc"})  
        return Response({"error": False, "message": f"Xuat Thuoc Thanh Cong: {so_luong} {thuoc[0].ten_thuoc}"})
    except:
        
        return Response({"error": True, "message": "Loi Tao Log Thuoc"})

class ThanhToanHoaDonThuocToggle(APIView):

    def get(self, request, format=None):
        id_don_thuoc    = request.GET.get('id', None)
        don_thuoc       = DonThuoc.objects.get(id = id_don_thuoc)
        danh_sach_thuoc = don_thuoc.ke_don.all()
        tong_tien       = request.GET.get('tong_tien', None)
        print(tong_tien)
        now             = datetime.now()
        date_time       = now.strftime("%m%d%y%H%M%S")
        ma_hoa_don      = "HDT-" + date_time
        
        hoa_don_thuoc = HoaDonThuoc.objects.create(don_thuoc=don_thuoc, ma_hoa_don=ma_hoa_don, tong_tien=tong_tien)
        try:
            for instance in danh_sach_thuoc:    
                id_thuoc = instance.thuoc.id 
                so_luong = instance.so_luong
                thuoc = Thuoc.objects.get(id=id_thuoc)
                ten_thuoc = thuoc.ten_thuoc

                xuat(request, id=id_thuoc, so_luong=so_luong)
            trang_thai = TrangThaiDonThuoc.objects.get_or_create(trang_thai="Đã Thanh Toán")[0]
            don_thuoc.trang_thai=trang_thai
            don_thuoc.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"charge_prescription_user_{don_thuoc.benh_nhan.id}", {
                    'type':'charge_prescription_notification'
                }
            )
            
            response = {'status': 200, 'message': 'Thanh Toán Thành Công'}
            return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
        except:
            response = {'status': 404, 'message': 'Xảy Ra Lỗi Trong Quá Trình Thanh Toán'}
            return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

class ThanhToanHoaDonDichVuToggle(APIView):
    def get(self, request, format=None):
        ma_hoa_don                = request.GET.get('ma_hoa_don', None)
        hoa_don_dich_vu           = HoaDonChuoiKham.objects.get(ma_hoa_don = ma_hoa_don)
        tong_tien                 = request.GET.get('tong_tien', None)
        hoa_don_dich_vu.tong_tien = tong_tien
        hoa_don_dich_vu.save()

        # Set trạng thái chuỗi khám
        trang_thai_chuoi_kham = TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham = "Đã Thanh Toán")[0]
        chuoi_kham = hoa_don_dich_vu.chuoi_kham
        chuoi_kham.trang_thai = trang_thai_chuoi_kham
        chuoi_kham.save()
        
        # Set trạng thái lịch hẹn
        lich_hen = chuoi_kham.lich_hen
        trang_thai_lich_hen = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Đã Thanh Toán Dịch Vụ")[0]
        lich_hen.trang_thai = trang_thai_lich_hen
        lich_hen.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"charge_process_bill_{chuoi_kham.benh_nhan.id}", {
                'type':'charge_process_bill_notification'
            }
        )
        
        response = {
            'status' : 200 ,
            'message': "Thanh Toán Thành Công!"
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

def thanh_toan_hoa_don_thuoc(request):
    id_don_thuoc = request.GET.get('id', None)
    tong_tien = request.GET.get('tong_tien', None)
    print(tong_tien)
    don_thuoc = DonThuoc.objects.get(id = id_don_thuoc)
    danh_sach_thuoc = don_thuoc.ke_don.all()
    now = datetime.now()
    date_time = now.strftime("%m%d%y%H%M%S")
    ma_hoa_don = "HDT-" + date_time
    print(ma_hoa_don)
    
    try:
        for instance in danh_sach_thuoc:    
            id_thuoc = instance.thuoc.id
            so_luong = instance.so_luong
            thuoc = Thuoc.objects.get(id=id_thuoc)
            ten_thuoc = thuoc.ten_thuoc
            if thuoc.kha_dung:
                thuoc.update(so_luong_kha_dung = F('so_luong_kha_dung') - so_luong)
                thuoc.save()
                ThuocLog.objects.create(thuoc=thuoc, ngay=timezone.now(), quy_trinh=ThuocLog.OUT, so_luong=so_luong)
            else:
                response = {'status': 404, 'message': f'Số Lượng Thuốc Không Khả Dụng, Vui Lòng Kiểm Tra Lại Thuốc: {ten_thuoc}'}
                return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
        
        hoa_don_thuoc = don_thuoc.hoa_don_thuoc
        hoa_don_thuoc.ma_hoa_don = ma_hoa_don
        hoa_don_thuoc.save()
        trang_thai = TrangThaiDonThuoc.objects.get_or_create(trang_thai="Đã Thanh Toán")[0]
        don_thuoc.update(trang_thai=trang_thai)
        don_thuoc.save()
        
        response = {'status': 200, 'message': 'Thanh Toán Thành Công'}
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
    except:
        response = {'status': 404, 'message': 'Xảy Ra Lỗi Trong Quá Trình Thanh Toán'}
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

def loginUser(request):
    so_dien_thoai = request.POST.get('so_dien_thoai')
    password = request.POST.get('password')
    
    user = authenticate(so_dien_thoai=so_dien_thoai, password=password)
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            return HttpResponse(json.dumps({'message': 'Success', 'url': '/trang_chu'}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'message': 'inactive'}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'message': 'invalid'}), content_type="application/json")

def dung_kham(request):
    if request.method == "POST":
        id_chuoi_kham = request.POST.get('id_chuoi_kham')
        ly_do = request.POST.get('ly_do')
        chuoi_kham = ChuoiKham.objects.get(id = id_chuoi_kham)
        trang_thai = TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham = "Dừng khám")[0]
        lich_su = LichSuChuoiKham.objects.create(chuoi_kham = chuoi_kham, trang_thai = trang_thai, chi_tiet_trang_thai = ly_do)
        chuoi_kham.trang_thai = trang_thai
        chuoi_kham.save()
        return HttpResponse(json.dumps({
            'status' : 200,
            'message' : "Đã dừng khám",
            'url': '/danh_sach_benh_nhan_cho'
        }), content_type="application/json")

# TODO Sửa lại phần dừng khám của bác sĩ lâm sàng, vì còn liên quan đến phần lịch hẹn

def dung_kham_chuyen_khoa(request):
    if request.method == "POST":
        id_chuoi_kham = request.POST.get('id_chuoi_kham')
        id_phan_khoa = request.POST.get('id_phan_khoa')
        ly_do = request.POST.get('ly_do')
        chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
        phan_khoa_kham = PhanKhoaKham.objects.get(id=id_phan_khoa)
        trang_thai = TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham = "Dừng khám")[0]
        trang_thai_phan_khoa = TrangThaiKhoaKham.objects.get_or_create(trang_thai_khoa_kham = "Dừng khám")[0]
        chuoi_kham.trang_thai = trang_thai
        chuoi_kham.save()
        phan_khoa_kham.trang_thai = trang_thai_phan_khoa
        phan_khoa_kham.save()
        lich_su_phan_khoa = LichSuTrangThaiKhoaKham.objects.create(phan_khoa_kham=phan_khoa_kham, trang_thai_khoa_kham=trang_thai_phan_khoa, chi_tiet_trang_thai=ly_do)
        lich_su_chuoi_kham = LichSuChuoiKham.objects.create(chuoi_kham=chuoi_kham, trang_thai=trang_thai,chi_tiet_trang_thai=ly_do)
        return HttpResponse(json.dumps({
            'status' : 200,
            'message' : "Đã dừng khám",
            'url': '/phong_chuyen_khoa'
        }), content_type="application/json")

# def xoa_lich_hen(request):
#     if request.method == "POST":
#         id_lich_hen = request.POST.get('id')
#         lich_hen = LichHenKham.objects.get(id=id_lich_hen)
#         lich_hen.delete()
#         return HttpResponse(json.dumps({
#             'status' : 200,
#             'url': '/danh_sach_lich_hen'
#         }), content_type="application/json")

@login_required(login_url='/dang_nhap/')
def update_nguon_cung(request, **kwargs):
    id_cong_ty = kwargs.get('id')
    instance = get_object_or_404(CongTy, id=id_cong_ty)
    form = CongTyForm(request.POST or None, instance=instance)
    phong_chuc_nang = PhongChucNang.objects.all()

    data = {
        'form': form,
        'id_cong_ty': id_cong_ty,
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'phong_tai_chinh/update_nguon_cung.html', context=data)


def chinh_sua_nguon_cung(request):
    if request.method == "POST":
        id_cong_ty = request.POST.get('id_cong_ty')
        ten_cong_ty = request.POST.get('ten_cong_ty')
        dia_chi = request.POST.get('dia_chi')
        giay_phep_kinh_doanh = request.POST.get('giay_phep_kinh_doanh')
        so_lien_lac = request.POST.get('so_lien_lac')
        email = request.POST.get('email')
        mo_ta = request.POST.get('mo_ta')
        cong_ty = get_object_or_404(CongTy, id=id_cong_ty)
        cong_ty.ten_cong_ty = ten_cong_ty
        cong_ty.dia_chi = dia_chi
        cong_ty.giay_phep_kinh_doanh = giay_phep_kinh_doanh
        cong_ty.so_lien_lac = so_lien_lac
        cong_ty.email = email
        cong_ty.mo_ta = mo_ta
        cong_ty.save()

        response = {
            'status': 200,
            'message': 'Cập Nhật Thông Tin Thành Công'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

@login_required(login_url='/dang_nhap/')
def danh_sach_dich_vu_kham(request):
    phong_chuc_nang = PhongChucNang.objects.all()

    return render(request, 'phong_tai_chinh/dich_vu_kham.html', context = {'phong_chuc_nang': phong_chuc_nang})

@login_required(login_url='/dang_nhap/')
def update_dich_vu_kham(request, **kwargs):
    id = kwargs.get('id')
    print(id)
    instance = get_object_or_404(DichVuKham, id=id)
    dich_vu_kham_form = DichVuKhamForm(request.POST or None, instance=instance)
    phong_chuc_nang = PhongChucNang.objects.all()

    data = {
        'dich_vu_kham_form': dich_vu_kham_form,
        'id'               : id,
        'phong_chuc_nang' : phong_chuc_nang
    }
    return render(request, 'phong_tai_chinh/update_dich_vu_kham.html', context=data)

def store_update_dich_vu_kham(request):
    if request.method == 'POST':
        id               = request.POST.get('id')
        ma_dvkt          = request.POST.get('ma_dvkt')
        ten_dvkt         = request.POST.get('ten_dvkt')
        ma_gia           = request.POST.get('ma_gia')
        don_gia          = request.POST.get('don_gia')
        quyet_dinh       = request.POST.get('quyet_dinh')
        cong_bo          = request.POST.get('cong_bo')
        id_phong_chuc_nang = request.POST.get('id_phong_chuc_nang')

        id_phong_chuc_nang = PhongChucNang.objects.get(id=id_phong_chuc_nang)
        
        dich_vu_kham = get_object_or_404(DichVuKham, id=id)
        dich_vu_kham.ma_dvkt          = ma_dvkt
        dich_vu_kham.ten_dvkt         = ten_dvkt
        dich_vu_kham.ma_gia           = ma_gia
        dich_vu_kham.don_gia          = don_gia
        dich_vu_kham.cong_bo          = cong_bo
        dich_vu_kham.quyet_dinh       = quyet_dinh
        dich_vu_kham.id_phong_chuc_nang = id_phong_chuc_nang
        dich_vu_kham.save()
        
        response = {
            'status': 200,
            'message': 'Cập Nhật Thông Tin Thành Công'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")


def chinh_sua_phong_chuc_nang(request):
    if request.method == "POST":
        id  = request.POST.get('id')
        ten_phong_chuc_nang = request.POST.get('ten_phong_chuc_nang')
        
        phong_chuc_nang = get_object_or_404(PhongChucNang, id=id)
        phong_chuc_nang.ten_phong_chuc_nang = ten_phong_chuc_nang
        phong_chuc_nang.save()

        response = {
            'status': 200,
            'message': 'Cập Nhật Thông Tin Thành Công'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

@login_required(login_url='/dang_nhap/')
def update_user(request, **kwargs):
    id_user = kwargs.get('id')
    instance = get_object_or_404(User, id=id_user)
    form = UserForm(request.POST or None, instance=instance)
    phong_chuc_nang = PhongChucNang.objects.all()

    data = {
        'form': form,
        'id_user': id_user,
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'update_user.html', context=data)

def cap_nhat_user(request):
    if request.method == "POST":
        id_user       = request.POST.get('id_user')
        ho_ten        = request.POST.get('ho_ten')
        email         = request.POST.get('email')
        so_dien_thoai = request.POST.get('so_dien_thoai')
        cmnd_cccd     = request.POST.get('cmnd')
        user = get_object_or_404(User, id=id_user)
        user.ho_ten        = ho_ten
        user.so_dien_thoai = so_dien_thoai
        user.email         = email
        user.cmnd_cccd     = cmnd_cccd
        user.save()

        response = {
            'status': 200,
            'message': 'Cập Nhật Thông Tin Thành Công'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

@login_required(login_url='/dang_nhap/')
def chinh_sua_thuoc(request, **kwargs):
    id_thuoc = kwargs.get('id_thuoc')
    instance = get_object_or_404(Thuoc, id=id_thuoc)
    phong_chuc_nang = PhongChucNang.objects.all()
    form = ThuocForm(request.POST or None, instance=instance)
    data = {
        'form': form,
        'id_thuoc': id_thuoc,
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'phong_tai_chinh/update_thuoc.html', context=data)

def update_thuoc(request):
    if request.method == "POST":
        id_thuoc          = request.POST.get('id_thuoc')
        ma_hoat_chat      = request.POST.get('ma_hoat_chat')
        ten_hoat_chat     = request.POST.get('ten_hoat_chat')
        ma_thuoc          = request.POST.get('ma_thuoc')
        ten_thuoc         = request.POST.get('ten_thuoc')
        ham_luong         = request.POST.get('ham_luong')
        duong_dung        = request.POST.get('duong_dung')
        so_dang_ky        = request.POST.get('so_dang_ky')
        dong_goi          = request.POST.get('dong_goi')
        don_vi_tinh       = request.POST.get('don_vi_tinh')
        don_gia           = request.POST.get('don_gia')
        don_gia_tt        = request.POST.get('don_gia_tt')
        so_lo             = request.POST.get('so_lo')
        so_luong_kha_dung = request.POST.get('so_luong_kha_dung')
        hang_sx           = request.POST.get('hang_sx')
        nuoc_sx           = request.POST.get('nuoc_sx')
        quyet_dinh        = request.POST.get('quyet_dinh')
        loai_thuoc        = request.POST.get('loai_thuoc')
        cong_bo           = request.POST.get('cong_bo')
        han_su_dung       = request.POST.get('han_su_dung')
        ngay_san_xuat     = request.POST.get('ngay_san_xuat')
        id_cong_ty        = request.POST.get('id_cong_ty')

        han_su_dung = datetime.strptime(han_su_dung, format_3)
        han_su_dung = han_su_dung.strftime("%Y-%m-%d")

        ngay_san_xuat = datetime.strptime(ngay_san_xuat, format_3)
        ngay_san_xuat = ngay_san_xuat.strftime("%Y-%m-%d")

        id_cong_ty = CongTy.objects.get(id = id_cong_ty)
        thuoc = get_object_or_404(Thuoc, id = id_thuoc)
        thuoc.id_thuoc          = id_thuoc
        thuoc.ma_hoat_chat      = ma_hoat_chat
        thuoc.ten_hoat_chat     = ten_hoat_chat
        thuoc.ma_thuoc          = ma_thuoc
        thuoc.ten_thuoc         = ten_thuoc
        thuoc.ham_luong         = ham_luong
        thuoc.duong_dung        = duong_dung
        thuoc.so_dang_ky        = so_dang_ky
        thuoc.dong_goi          = dong_goi
        thuoc.don_vi_tinh       = don_vi_tinh
        thuoc.don_gia           = don_gia
        thuoc.don_gia_tt        = don_gia_tt
        thuoc.so_lo             = so_lo
        thuoc.so_luong_kha_dung = so_luong_kha_dung
        thuoc.hang_sx           = hang_sx
        thuoc.nuoc_sx           = nuoc_sx
        thuoc.quyet_dinh        = quyet_dinh
        thuoc.loai_thuoc        = loai_thuoc
        thuoc.cong_bo           = cong_bo
        thuoc.han_su_dung       = han_su_dung
        thuoc.ngay_san_xuat     = ngay_san_xuat
        thuoc.cong_ty           = id_cong_ty
        thuoc.save()

        response = {
            'status': 200,
            'message': 'Cập Nhật Thông Tin Thành Công'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

@login_required(login_url='/dang_nhap/')
def chinh_sua_thuoc_phong_thuoc(request, **kwargs):
    id_thuoc = kwargs.get('id_thuoc')
    instance = get_object_or_404(Thuoc, id=id_thuoc)
    form = ThuocForm(request.POST or None, instance=instance)
    phong_chuc_nang = PhongChucNang.objects.all()

    data = {
        'form': form,
        'id_thuoc': id_thuoc,
        'phong_chuc_nang' : phong_chuc_nang
    }
    return render(request, 'phong_thuoc/update_thuoc.html', context=data)


def update_thuoc_phong_thuoc(request):
    if request.method == "POST":
        id_thuoc          = request.POST.get('id_thuoc')
        ma_hoat_chat      = request.POST.get('ma_hoat_chat')
        ten_hoat_chat     = request.POST.get('ten_hoat_chat')
        ma_thuoc          = request.POST.get('ma_thuoc')
        ten_thuoc         = request.POST.get('ten_thuoc')
        ham_luong         = request.POST.get('ham_luong')
        duong_dung        = request.POST.get('duong_dung')
        so_dang_ky        = request.POST.get('so_dang_ky')
        dong_goi          = request.POST.get('dong_goi')
        don_vi_tinh       = request.POST.get('don_vi_tinh')
        so_lo             = request.POST.get('so_lo')
        so_luong_kha_dung = request.POST.get('so_luong_kha_dung')
        hang_sx           = request.POST.get('hang_sx')
        nuoc_sx           = request.POST.get('nuoc_sx')
        quyet_dinh        = request.POST.get('quyet_dinh')
        loai_thuoc        = request.POST.get('loai_thuoc')
        cong_bo           = request.POST.get('cong_bo')
        han_su_dung       = request.POST.get('han_su_dung')
        ngay_san_xuat     = request.POST.get('ngay_san_xuat')

        han_su_dung = datetime.strptime(han_su_dung, format_2)
        han_su_dung = han_su_dung.strftime("%Y-%m-%d")

        ngay_san_xuat = datetime.strptime(ngay_san_xuat, format_2)
        ngay_san_xuat = ngay_san_xuat.strftime("%Y-%m-%d")

        thuoc = get_object_or_404(Thuoc, id = id_thuoc)
        thuoc.id_thuoc          = id_thuoc
        thuoc.ma_hoat_chat      = ma_hoat_chat
        thuoc.ten_hoat_chat     = ten_hoat_chat
        thuoc.ma_thuoc          = ma_thuoc
        thuoc.ten_thuoc         = ten_thuoc
        thuoc.ham_luong         = ham_luong
        thuoc.duong_dung        = duong_dung
        thuoc.so_dang_ky        = so_dang_ky
        thuoc.dong_goi          = dong_goi
        thuoc.don_vi_tinh       = don_vi_tinh
        thuoc.so_lo             = so_lo
        thuoc.so_luong_kha_dung = so_luong_kha_dung
        thuoc.hang_sx           = hang_sx
        thuoc.nuoc_sx           = nuoc_sx
        thuoc.quyet_dinh        = quyet_dinh
        thuoc.loai_thuoc        = loai_thuoc
        thuoc.cong_bo           = cong_bo
        thuoc.han_su_dung       = han_su_dung
        thuoc.ngay_san_xuat     = ngay_san_xuat
        thuoc.save()

        response = {
            'status': 200,
            'message': 'Cập Nhật Thông Tin Thành Công'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

@login_required(login_url='/dang_nhap/')    
def doanh_thu_phong_kham(request):
    phong_chuc_nang = PhongChucNang.objects.all()
    
    return render(request, 'phong_tai_chinh/doanh_thu_phong_kham.html', context = {'phong_chuc_nang': phong_chuc_nang})

@login_required(login_url='/dang_nhap/')
def them_dich_vu_kham_excel(request):
    phong_chuc_nang = PhongChucNang.objects.all()

    data = {
        'phong_chuc_nang': phong_chuc_nang,
    }
    return render(request, 'phong_tai_chinh/them_dich_vu_kham_excel.html', context=data)

@login_required(login_url='/dang_nhap/')
def them_dich_vu_kham(request):
    '''Đây là trường hợp "and"'''
    # bac_si = User.objects.filter(Q(chuc_nang = 4) | Q(chuc_nang = 3))
    bac_si = User.objects.filter(chuc_nang = 4)
    phong_chuc_nang = PhongChucNang.objects.all()

    data = {
        'bac_si': bac_si,
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'phong_tai_chinh/them_dich_vu_kham.html', context=data)


from decimal import Decimal
def import_dich_vu_excel(request):
    if request.method == 'POST':
        data             = request.POST.get('data')  
        list_objects     = json.loads(data)
        
        bulk_create_data = []
        print(list_objects)
        for obj in list_objects:
            stt             = obj['STT']
            ma_gia_key      = "MA_GIA"
            ma_cosokcb_key  = "MA_COSOKCB"
            ma_dvkt         = obj['MA_DVKT']
            ten_dvkt        = obj['TEN_DVKT']
            don_gia         = "DON_GIA"
            
            bao_hiem        = True
            quyet_dinh      = obj['QUYET_DINH']
            cong_bo         = obj['CONG_BO']
            phong_chuc_nang = obj['PHONG_CHUC_NANG']

            group_phong_chuc_nang = PhongChucNang.objects.get_or_create(ten_phong_chuc_nang = phong_chuc_nang)[0]

            if ma_gia_key in obj.keys():
                ma_gia = obj[ma_gia_key]
            else:
                ma_gia = ""

            if ma_cosokcb_key in obj.keys():
                ma_cosokcb = obj[ma_cosokcb_key]
            else:
                ma_cosokcb = ""

            if don_gia in obj.keys():
                don_gia = obj[don_gia]
                gia     = Decimal(don_gia)
            else:
                gia=0

                
            # print(ma_gia)
            model = DichVuKham(
                stt             = stt,
                ma_dvkt         = ma_dvkt,
                ten_dvkt        = ten_dvkt,
                ma_gia          = ma_gia,
                don_gia         = gia,
                bao_hiem        = bao_hiem,
                quyet_dinh      = quyet_dinh,
                cong_bo         = cong_bo,
                ma_cosokcb      = ma_cosokcb,
                phong_chuc_nang = group_phong_chuc_nang
            )
            bulk_create_data.append(model)
        
        DichVuKham.objects.bulk_update_or_create(bulk_create_data,[
            'stt',
            'ma_dvkt',
            'ten_dvkt',
            'ma_gia',
            'don_gia',
            'bao_hiem',
            'quyet_dinh',
            'cong_bo',
            'ma_cosokcb',
            'phong_chuc_nang' 
        ], match_field = 'stt', batch_size=10)

        response = {
            'status': 200,
            'message': 'Import Thanh Cong',
            'url' : '/danh_sach_dich_vu_kham/'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
    else:
        response = {
            'status': 404,
            'message': 'That Bai',
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

@login_required(login_url='/dang_nhap/')      
def them_thuoc_excel(request):
    phong_chuc_nang = PhongChucNang.objects.all()

    return render(request, 'phong_tai_chinh/them_thuoc_excel.html', context = {'phong_chuc_nang': phong_chuc_nang})

def import_thuoc_excel(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        list_objects = json.loads(data)
        bulk_create_data = []

        for obj in list_objects:
            ma_thuoc_key      = "MA_THUOC_BV"
            ma_hoat_chat_key  = "MA_HOAT_CHAT"
            ma_cskcb_key      = "MA_CSKCB"
            ten_hoat_chat     = obj['HOAT_CHAT']
            duong_dung_key    = "DUONG_DUNG"
            ham_luong_key     = "HAM_LUONG"
            ten_thuoc         = obj['TEN_THUOC']
            so_dang_ky        = obj['SO_DANG_KY']
            dong_goi          = obj['DONG_GOI']
            don_vi_tinh       = obj['DON_VI_TINH']
            don_gia           = Decimal(obj['DON_GIA'])
            don_gia_tt        = Decimal(obj['DON_GIA_TT'])
            so_luong_kha_dung = obj['SO_LUONG']
            hang_sx           = obj['HANG_SX']
            nuoc_sx_key       = "NUOC_SX"
            quyet_dinh        = obj['QUYET_DINH']
            cong_bo           = obj['CONG_BO']
            loai_thuoc        = obj['LOAI_THUOC']
            loai_thau         = obj['LOAI_THAU']
            nhom_thau         = obj['NHOM_THAU']
            nha_thau          = obj['NHA_THAU']
            bao_hiem          = True

            group_nhom_thau = NhomThau.objects.get_or_create(ten_nhom_thau=nhom_thau)[0]
            group_cong_ty = CongTy.objects.get_or_create(ten_cong_ty=nha_thau)[0]
            

            if ma_hoat_chat_key in obj.keys():
                ma_hoat_chat = obj[ma_hoat_chat_key]
            else:
                ma_hoat_chat = ""

            if ma_cskcb_key in obj.keys():
                ma_cskcb = obj[ma_cskcb_key]
            else:
                ma_cskcb = ""

            if nuoc_sx_key in obj.keys():
                nuoc_sx = obj[nuoc_sx_key]
            else: 
                nuoc_sx = ""

            if ma_thuoc_key in obj.keys():
                ma_thuoc = obj[ma_thuoc_key]
            else:
                ma_thuoc = ""

            if duong_dung_key in obj.keys():
                duong_dung = obj[duong_dung_key]
            else:
                duong_dung = ""

            if ham_luong_key in obj.keys():
                ham_luong = obj[ham_luong_key]
            else:
                ham_luong = ""

            model = Thuoc(
                ma_thuoc          = ma_thuoc,
                ma_hoat_chat      = ma_hoat_chat, 
                ten_hoat_chat     = ten_hoat_chat, 
                duong_dung        = duong_dung,
                ham_luong         = ham_luong,
                ten_thuoc         = ten_thuoc,
                so_dang_ky        = so_dang_ky, 
                dong_goi          = dong_goi,
                don_vi_tinh       = don_vi_tinh,
                don_gia           = don_gia,
                don_gia_tt        = don_gia_tt,
                so_lo             = "",
                so_luong_kha_dung = so_luong_kha_dung,
                ma_cskcb          = ma_cskcb, 
                hang_sx           = hang_sx,
                nuoc_sx           = nuoc_sx,
                quyet_dinh        = quyet_dinh, 
                loai_thuoc        = loai_thuoc, 
                cong_bo           = cong_bo,
                loai_thau         = loai_thau,
                nhom_thau         = group_nhom_thau,
                cong_ty           = group_cong_ty,
                bao_hiem          = bao_hiem
            )

            bulk_create_data.append(model)

        Thuoc.objects.bulk_update_or_create(bulk_create_data, [
            'ma_hoat_chat', 
            'ten_hoat_chat', 
            'duong_dung', 
            'ham_luong', 
            'ten_thuoc', 
            'so_dang_ky', 
            'dong_goi', 
            'don_vi_tinh', 
            'don_gia', 
            'don_gia_tt',
            'so_luong_kha_dung',
            'ma_cskcb',
            'hang_sx',
            'nuoc_sx',
            'quyet_dinh',
            'cong_bo',
            'loai_thau',
            'nhom_thau'
        ], match_field = 'ma_thuoc')
        response = {
            'status': 200,
            'message': 'Import Thanh Cong'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
        
def store_cong_ty(request):
    if request.method == 'POST':
        ten_cong_ty          = request.POST.get('ten_cong_ty')
        giay_phep_kinh_doanh = request.POST.get('giay_phep_kinh_doanh')
        so_lien_lac          = request.POST.get('so_lien_lac')
        email                = request.POST.get('email')
        dia_chi              = request.POST.get('dia_chi')

        CongTy.objects.get_or_create(
            ten_cong_ty          = ten_cong_ty,
            giay_phep_kinh_doanh = giay_phep_kinh_doanh,
            so_lien_lac          = so_lien_lac,
            email                = email,
            dia_chi              = dia_chi,
        )[0]

        response = {
            "message" : "Them Thanh Cong",
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

@login_required(login_url='/dang_nhap/')
def danh_sach_bai_dang(request):
    phong_chuc_nang = PhongChucNang.objects.all()

    return render(request, "le_tan/danh_sach_bai_dang.html", context={'phong_chuc_nang':phong_chuc_nang})

def store_thanh_toan_lam_sang(request):
    if request.method == 'POST':
        id_lich_hen = request.POST.get('id')
        gia_tien = request.POST.get('gia_tien')

        lich_hen = LichHenKham.objects.get(id = id_lich_hen)
        print(id_lich_hen)
        hoa_don_lam_sang = HoaDonLamSang.objects.create(
            tong_tien = gia_tien, 
            lich_hen = lich_hen
        )
        trang_thai = TrangThaiLichHen.objects.get_or_create(ten_trang_thai = "Đã Thanh Toán Lâm Sàng")[0]
        lich_hen.trang_thai = trang_thai
        lich_hen.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"charge_bill_user_{lich_hen.benh_nhan.id}", {
                'type':'charge_bill_notification'
            }
        )

        HoaDonTong.objects.get_or_create(hoa_don_lam_sang = hoa_don_lam_sang, lich_hen = lich_hen)[0]

        response = {
            'status': 200,
            'message': 'Thanh Toán Lâm Sàng Thành Công'
        }
        # return redirect('/danh_sach_benh_nhan/')
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

@login_required(login_url='/dang_nhap/')
def danh_sach_phong_chuc_nang(request):
    phong_chuc_nang = PhongChucNang.objects.all()
    bac_si_phu_trach = User.objects.filter(chuc_nang = 4)
    data = {
        'bac_si_phu_trach' : bac_si_phu_trach,
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'le_tan/danh_sach_phong_chuc_nang.html', context=data)

@login_required(login_url='/dang_nhap/')
def them_phong_chuc_nang(request):
    bac_si_phu_trach = User.objects.filter(chuc_nang=4)
    phong_chuc_nang = PhongChucNang.objects.all()

    data = {
        'bac_si_phu_trach' : bac_si_phu_trach,
        'phong_chuc_nang' : phong_chuc_nang
    }
    return render(request, 'le_tan/them_phong_chuc_nang.html', context=data)


def them_pcn_kem_dich_vu(request):
    if request.method == "POST":
        ten_phong_chuc_nang = request.POST.get("ten_phong_chuc_nang")
        id_bac_si           = request.POST.get('bac_si_phu_trach') # phan nay la phan id bac si m gui len o template, dat ten nao thi tuy
        request_data        = request.POST.get('data')
        data                = json.loads(request_data)
 
        bac_si_phu_trach = User.objects.get(id=id_bac_si)
        phong_chuc_nang = PhongChucNang.objects.create(ten_phong_chuc_nang=ten_phong_chuc_nang, bac_si_phu_trach=bac_si_phu_trach)
        
        list_id_dich_vu_kham = []
 
        for obj in data:
            id = obj['obj']['id']
            list_id_dich_vu_kham.append(id) # lay tat ca id cua dich vu kham va append vao list
 
        danh_sach_dich_vu = DichVuKham.objects.filter(id__in=list_id_dich_vu_kham) # filter tat ca dich vu co id nam trong               list_id_dich_vu_kham

        for dich_vu in danh_sach_dich_vu:
            dich_vu.phong_chuc_nang = phong_chuc_nang # cap nhat field phong_chuc_nang cho tung dich_vu
        DichVuKham.objects.bulk_update(danh_sach_dich_vu, ['phong_chuc_nang']) # update tat ca cac ban ghi o tren bang 1 query
        
        response = {
            'status': 200,
            'message': 'Thêm Phòng Chức Năng Thành Công'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

@login_required(login_url='/dang_nhap/')
def update_phong_chuc_nang(request, **kwargs):
    id_phong_chuc_nang = kwargs.get('id')
    instance = get_object_or_404(PhongChucNang, id=id_phong_chuc_nang)
    phong_chuc_nang = PhongChucNang.objects.all()
    form = PhongChucNangForm(request.POST or None, instance=instance)
    data = {
        'form': form,
        'id_phong_chuc_nang': id_phong_chuc_nang,
        'phong_chuc_nang': phong_chuc_nang
    }
    return render(request, 'le_tan/update_phong_chuc_nang.html', context=data)

@login_required(login_url='/dang_nhap/')
def them_bai_dang(request):
    phong_chuc_nang = PhongChucNang.objects.all()

    return render(request, 'le_tan/them_bai_dang.html',context ={'phong_chuc_nang' : phong_chuc_nang})

def upload_bai_dang(request):
    print(request.FILES)
    if request.method == "POST":
        tieu_de            = request.POST.get('tieu_de', None)
        noi_dung_chinh     = request.POST.get('noi_dung_chinh', None)
        noi_dung           = request.POST.get('noi_dung', None)
        thoi_gian_bat_dau  = request.POST.get('thoi_gian_bat_dau', None)
        thoi_gian_ket_thuc = request.POST.get('thoi_gian_ket_thuc')
        print(thoi_gian_bat_dau)
        thoi_gian_bat_dau = datetime.strptime(thoi_gian_bat_dau, format_2)
        thoi_gian_bat_dau = thoi_gian_bat_dau.strftime("%Y-%m-%d %H:%M")

        thoi_gian_ket_thuc = datetime.strptime(thoi_gian_ket_thuc, format_2)
        thoi_gian_ket_thuc = thoi_gian_ket_thuc.strftime("%Y-%m-%d %H:%M")
        # print(id_chuoi_kham)

        if tieu_de == '':
            HttpResponse({'status': 404, 'message': 'Mã Kết Quả Không Được Để Trống'})

        if noi_dung_chinh == '':
            HttpResponse({'status': 404, 'message': 'Mô Tả Không Được Để Trống'})

        # chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
        # ket_qua_tong_quat = KetQuaTongQuat.objects.get_or_create(chuoi_kham=chuoi_kham)[0]
        # ket_qua_chuyen_khoa = KetQuaChuyenKhoa.objects.create(ket_qua_tong_quat=ket_qua_tong_quat, ma_ket_qua=ma_ket_qua, mo_ta=mo_ta, ket_luan=ket_luan)
        
        for value in request.FILES.values():
            
            bai_dang = BaiDang.objects.create(
                tieu_de            = tieu_de,
                noi_dung_chinh     = noi_dung_chinh,
                noi_dung           = noi_dung,
                thoi_gian_bat_dau  = thoi_gian_bat_dau,
                thoi_gian_ket_thuc = thoi_gian_ket_thuc,
                hinh_anh           = value,
                nguoi_dang_bai     = request.user,
            )
            bai_dang.save()
            # file = BaiDang.objects.create(file=value)
            # file_kq_chuyen_khoa = FileKetQuaChuyenKhoa.objects.create(ket_qua_chuyen_khoa=ket_qua_chuyen_khoa, file=file)
        
        return HttpResponse('upload')
    response = {
        'status': 200,
        'message' : 'Upload Thành Công!'
    }
    return HttpResponse(json.dumps(response), content_type='application/json; charset=utf-8')

@login_required(login_url='/dang_nhap/')
def chi_tiet_bai_dang(request, **kwargs):
    id_bai_dang = kwargs.get('id')
    bai_dang = BaiDang.objects.get(id = id_bai_dang)
    phong_chuc_nang = PhongChucNang.objects.all()

    data = {
        'bai_dang': bai_dang,
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'le_tan/bai_dang.html', context=data)

@login_required(login_url='/dang_nhap/')
def update_don_thuoc(request, **kwargs):
    id_don_thuoc = kwargs.get('id')
    don_thuoc = DonThuoc.objects.get(id = id_don_thuoc)
    danh_sach_thuoc = don_thuoc.ke_don.all()
    phong_chuc_nang = PhongChucNang.objects.all()

    data = {
        'danh_sach_thuoc': danh_sach_thuoc,
        'don_thuoc' : don_thuoc,
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'bac_si_lam_sang/update_don_thuoc.html', context=data)

@login_required(login_url='/dang_nhap/')
def danh_sach_vat_tu(request):
    phong_chuc_nang = PhongChucNang.objects.all()

    return render(request, 'phong_tai_chinh/danh_sach_vat_tu.html', context={'phong_chuc_nang': phong_chuc_nang})

@login_required(login_url='/dang_nhap/')
def them_vat_tu_excel(request):
    phong_chuc_nang = PhongChucNang.objects.all()

    return render(request, 'phong_tai_chinh/them_vat_tu_excel.html', context={'phong_chuc_nang':phong_chuc_nang})

# UPDATE
def import_vat_tu_excel(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        list_objects = json.loads(data)
        bulk_create_data = []

        for obj in list_objects:
            stt            = obj['MA']
            ma_nhom_vtyt   = obj['MA_NHOM_VTYT']
            ten_nhom_vtyt  = obj['TEN_NHOM_VTYT']
            ma_hieu        = obj['MA_HIEU']
            ma_vtyt_bv     = obj['MA_VTYT_BV']
            ten_vtyt_bv    = obj['TEN_VTYT_BV']
            quy_cach       = obj['QUY_CACH']
            hang_sx        = obj['HANG_SX']
            nuoc_sx        = obj['NUOC_SX']
            don_vi_tinh    = obj['DON_VI_TINH']
            don_gia        = Decimal(obj['DON_GIA'])
            don_gia_tt     = Decimal(obj['DON_GIA_TT'])
            nha_thau       = obj['NHA_THAU']
            quyet_dinh     = obj['QUYET_DINH']
            cong_bo        = obj['CONG_BO']
            dinh_muc       = obj['DINH_MUC']
            so_luong       = obj['SO_LUONG']
            loai_thau      = obj['LOAI_THAU']
            bao_hiem       = True

            group_cong_ty = CongTy.objects.get_or_create(ten_cong_ty=nha_thau)[0]
            group_nhom_vat_tu = NhomVatTu.objects.get_or_create(ma_nhom_vtyt = ma_nhom_vtyt, ten_nhom_vtyt = ten_nhom_vtyt)[0]
            
            model = VatTu(
                stt               = stt,
                nhom_vat_tu       = group_nhom_vat_tu,
                ma_hieu           = ma_hieu,
                ma_vtyt_bv        = ma_vtyt_bv,
                ten_vtyt_bv       = ten_vtyt_bv,
                quy_cach          = quy_cach,
                hang_sx           = hang_sx,
                nuoc_sx           = nuoc_sx,
                don_vi_tinh       = don_vi_tinh,
                don_gia           = don_gia,
                don_gia_tt        = don_gia_tt,
                nha_thau          = group_cong_ty,
                quyet_dinh        = quyet_dinh,
                cong_bo           = cong_bo,
                dinh_muc          = dinh_muc,
                so_luong_kha_dung = so_luong,
                loai_thau         = loai_thau,
                bao_hiem          = bao_hiem,
            )

            bulk_create_data.append(model)

        VatTu.objects.bulk_update_or_create(bulk_create_data, [
            'stt',
            'nhom_vat_tu',
            'ma_hieu',
            'ma_vtyt_bv',
            'ten_vtyt_bv',
            'quy_cach',
            'hang_sx',
            'nuoc_sx',
            'don_vi_tinh',
            'don_gia',
            'don_gia_tt',
            'nha_thau',
            'quyet_dinh',
            'cong_bo',
            'dinh_muc',
            'so_luong_kha_dung',
            'loai_thau',
            'bao_hiem',
        ], match_field = 'stt')

        response = {
            'status': 200,
            'message': 'Import Thanh Cong'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
# END

def nhan_don_thuoc(request):
    if request.method == 'POST':
        id = request.POST.get('id')

        trang_thai_don_thuoc = TrangThaiDonThuoc.objects.get_or_create(trang_thai = "Hoàn Thành")[0]
        don_thuoc = DonThuoc.objects.get(id=id)
        chuoi_kham = don_thuoc.chuoi_kham
        trang_thai_chuoi_kham = TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham = "Hoàn Thành")[0]
        chuoi_kham.trang_thai = trang_thai_chuoi_kham
        chuoi_kham.save()
        don_thuoc.trang_thai = trang_thai_don_thuoc
        don_thuoc.save()
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"process_accomplished_user_{don_thuoc.benh_nhan.id}", {
                'type':'process_accomplished_notification'
            }
        )

        response={
            'status' : 200,
            'message' : 'Đã Nhận Đơn Thuốc'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
        
def xoa_thuoc(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        thuoc = Thuoc.objects.get(id = id)
        thuoc.delete()

        response = {
            'thuoc' : thuoc.ten_thuoc
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

def xoa_dich_vu(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        DichVuKham.objects.get(id=id).delete()

        response = {
            'message' : "Xóa Thành Công"
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

def xoa_vat_tu(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        VatTu.objects.get(id=id).delete()

        response = {
            'message' : "Xóa Thành Công"
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

@login_required(login_url='/dang_nhap/')
def danh_sach_bac_si(request):
    phong_chuc_nang = PhongChucNang.objects.all()
    
    data={
        'phong_chuc_nang' : phong_chuc_nang,
    }

    return render(request, 'danh_sach_bac_si.html', context=data)

def create_bac_si(request):
    if request.method == "POST":
        ho_ten         = request.POST.get("ho_ten",         None)
        so_dien_thoai  = request.POST.get("so_dien_thoai",  None)
        password       = request.POST.get("password",       None)
        cmnd_cccd      = request.POST.get("cmnd_cccd",      None)
        dia_chi        = request.POST.get("dia_chi",        None)
        ngay_sinh      = request.POST.get("ngay_sinh",      None)
        gioi_tinh      = request.POST.get("gioi_tinh",      None)
        dan_toc        = request.POST.get("dan_toc",        None)
        ma_so_bao_hiem = request.POST.get("ma_so_bao_hiem", None)
        gioi_thieu     = request.POST.get('gioi_thieu',     None)
        chuc_danh      = request.POST.get('chuc_danh',      None)
        chuyen_khoa    = request.POST.get('chuyen_khoa',    None)
        noi_cong_tac   = request.POST.get('noi_cong_tac',   None)
        kinh_nghiem    = request.POST.get('kinh_nghiem',    None)
        loai_cong_viec = request.POST.get('loai_cong_viec', None)
        chuc_nang      = request.POST.get('chuc_nang',      None)


        ngay_sinh = datetime.strptime(ngay_sinh, format_3)
        ngay_sinh = ngay_sinh.strftime("%Y-%m-%d")
        
        if len(ho_ten) == 0:
            return HttpResponse(json.dumps({'message': "Họ Tên Không Được Trống", 'status': '400'}), content_type='application/json; charset=utf-8')

        if User.objects.filter(so_dien_thoai=so_dien_thoai).exists():
            return HttpResponse(json.dumps({'message': "Số Điện Thoại Đã Tồn Tại", 'status': '409'}), content_type='application/json; charset=utf-8')

        if User.objects.filter(cmnd_cccd=cmnd_cccd).exists():
            return HttpResponse(json.dumps({'message': "Số chứng minh thư đã tồn tại", 'status': '403'}), content_type = 'application/json; charset=utf-8')

        user = User.objects.create(
            ho_ten         = ho_ten, 
            so_dien_thoai  = so_dien_thoai, 
            password       = password,
            cmnd_cccd      = cmnd_cccd,
            dia_chi        = dia_chi,
            ngay_sinh      = ngay_sinh,
            gioi_tinh      = gioi_tinh,
            dan_toc        = dan_toc,    
            ma_so_bao_hiem = ma_so_bao_hiem,
            chuc_nang      = chuc_nang,
        )
        user.save()

        bac_si = BacSi.objects.create(
            user           = user,
            gioi_thieu     = gioi_thieu    ,
            chuc_danh      = chuc_danh     ,
            chuyen_khoa    = chuyen_khoa   ,
            noi_cong_tac   = noi_cong_tac  ,
            kinh_nghiem    = kinh_nghiem   ,
            loai_cong_viec = loai_cong_viec,
        )
        bac_si.save()

        response = {
            "message"      : "Thêm Mới Bác Sĩ Thành Công",
            "ho_ten"       : bac_si.user.ho_ten,
            "so_dien_thoai": bac_si.user.so_dien_thoai,
        }

        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

@login_required(login_url='/dang_nhap/')
def update_bac_si(request, **kwargs):
    id_bac_si = kwargs.get('id')
    instance = get_object_or_404(BacSi, id=id_bac_si)
    form = BacSiForm(request.POST or None, instance=instance)
    
    user_id = kwargs.get('user_id')
    instance_user = get_object_or_404(User, id=user_id)
    form_user = UserForm(request.POST or None, instance=instance_user)
    phong_chuc_nang = PhongChucNang.objects.all()
    data = {
        'id_bac_si': id_bac_si,
        'form': form,
        'user_id': user_id,
        'form_user': form_user,
        'phong_chuc_nang': phong_chuc_nang,
    }
    return render(request, 'update_bac_si.html', context=data)

def cap_nhat_thong_tin_bac_si(request):
    if request.method == "POST":
        id   = request.POST.get('id')
        user_id        = request.POST.get('user_id')
        ho_ten         = request.POST.get('ho_ten')
        so_dien_thoai  = request.POST.get('so_dien_thoai')
        cmnd_cccd      = request.POST.get('cmnd_cccd')
        ngay_sinh      = request.POST.get('ngay_sinh')
        gioi_thieu     = request.POST.get('gioi_thieu')
        noi_cong_tac   = request.POST.get('noi_cong_tac')
        chuyen_khoa    = request.POST.get('chuyen_khoa')
        chuc_danh      = request.POST.get('chuc_danh')
        loai_cong_viec = request.POST.get('loai_cong_viec')
        kinh_nghiem    = request.POST.get('kinh_nghiem')
        dia_chi        = request.POST.get('dia_chi')

        ngay_sinh = datetime.strptime(ngay_sinh, format_3)
        ngay_sinh = ngay_sinh.strftime("%Y-%m-%d")

        benh_nhan = get_object_or_404(User, id=user_id)
        benh_nhan.ho_ten         = ho_ten
        benh_nhan.so_dien_thoai  = so_dien_thoai
        benh_nhan.cmnd_cccd      = cmnd_cccd
        benh_nhan.dia_chi        = dia_chi
        benh_nhan.ngay_sinh      = ngay_sinh
        benh_nhan.save()

        bac_si = get_object_or_404(BacSi, id=id)
        bac_si.gioi_thieu     = gioi_thieu    
        bac_si.noi_cong_tac   = noi_cong_tac  
        bac_si.chuyen_khoa    = chuyen_khoa   
        bac_si.chuc_danh      = chuc_danh     
        bac_si.loai_cong_viec = loai_cong_viec
        bac_si.kinh_nghiem    = kinh_nghiem   
        bac_si.save()
        
        response = {
            'status': 200,
            'message': 'Cập Nhật Thông Tin Thành Công'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

def xoa_lich_hen(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        LichHenKham.objects.get(id = id).delete()

        response = {
            'message' : "Xóa Lịch Hẹn Thành Công!"
        }

        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

@login_required(login_url='/dang_nhap/')  
def xuat_bao_hiem(request):
    phong_chuc_nang = PhongChucNang.objects.all()

    data ={
        'phong_chuc_nang' : phong_chuc_nang,
    }

    return render(request, 'phong_tai_chinh/xuat_bao_hiem.html', context = data)

def upload_ket_qua_lam_sang(request):
    if request.method == "POST":
        ma_ket_qua    = request.POST.get('ma_ket_qua', None)
        mo_ta         = request.POST.get('mo_ta', None)
        ket_luan      = request.POST.get('ket_qua', None)
        id_chuoi_kham = request.POST.get('id_chuoi_kham')

        if ma_ket_qua == '':
            HttpResponse({'status': 404, 'message': 'Mã Kết Quả Không Được Để Trống'})

        if mo_ta == '':
            HttpResponse({'status': 404, 'message': 'Mô Tả Không Được Để Trống'})

        if ket_luan == '':
            HttpResponse({'status': 404, 'message': 'Kết Luận Không Được Để Trống'})

        chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
        ket_qua_tong_quat = KetQuaTongQuat.objects.get_or_create(chuoi_kham=chuoi_kham)[0]
        ket_qua_tong_quat.ma_ket_qua = ma_ket_qua
        ket_qua_tong_quat.mo_ta      = mo_ta
        ket_qua_tong_quat.ket_luan   = ket_luan
        ket_qua_tong_quat.save()

        response = {
            'message' : "Upload Kết Quả Thành Công!"
        }

        # return 
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

def upload_ket_qua_chuyen_khoa(request):
    if request.method == "POST":
        ma_ket_qua    = request.POST.get('ma_ket_qua', None)
        mo_ta         = request.POST.get('mo_ta', None)
        ket_luan      = request.POST.get('ket_qua', None)
        id_chuoi_kham = request.POST.get('id_chuoi_kham')

        if ma_ket_qua == '':
            HttpResponse({'status': 404, 'message': 'Mã Kết Quả Không Được Để Trống'})

        if mo_ta == '':
            HttpResponse({'status': 404, 'message': 'Mô Tả Không Được Để Trống'})

        if ket_luan == '':
            HttpResponse({'status': 404, 'message': 'Kết Luận Không Được Để Trống'})

        chuoi_kham = ChuoiKham.objects.get(id=id_chuoi_kham)
        ket_qua_tong_quat = KetQuaTongQuat.objects.get_or_create(chuoi_kham=chuoi_kham)[0]
        ket_qua_chuyen_khoa = KetQuaChuyenKhoa.objects.create(ket_qua_tong_quat=ket_qua_tong_quat, ma_ket_qua=ma_ket_qua, mo_ta=mo_ta, ket_luan=ket_luan)

        response = {
            'status': 200,
            'message' : 'Upload Thành Công!'
        }

        return HttpResponse(json.dumps(response), content_type='application/json; charset=utf-8')


# * --- update 6/1/2021 ---
@login_required(login_url='/dang_nhap/')
def thong_ke_vat_tu(request):
    phong_chuc_nang = PhongChucNang.objects.all()
    user_id = request.user.id

    data = {
        'phong_chuc_nang': phong_chuc_nang,
        'user_id'        : user_id,
    }
    return render(request, 'phong_tai_chinh/thong_ke_vat_tu_cuoi_thang.html', context=data)

def store_thong_ke_vat_tu(request):
    if request.method == "POST":
        request_data = request.POST.get('data', None)
        user = request.user
        data = json.loads(request_data)
        print(data)

        list_thanh_tien = []
        bulk_create_data = []

        for i in data:
            thanh_tien = int(i['obj']['thanh_tien'])
            list_thanh_tien.append(thanh_tien)
            
        tong_tien = int(sum(list_thanh_tien))
        hoa_don_vat_tu = HoaDonVatTu.objects.get_or_create(nguoi_phu_trach = user, tong_tien = tong_tien)[0]
        # hoa_don_vat_tu = HoaDonVatTu.objects.get_or_create
        hoa_don_vat_tu.save()
        for i in data:
            vat_tu = VatTu.objects.only('id').get(id=i['obj']['id'])    
            ke_don_thuoc = KeVatTu(vat_tu=vat_tu, so_luong=i['obj']['so_luong'], bao_hiem=i['obj']['bao_hiem'], hoa_don_vat_tu = hoa_don_vat_tu)
            bulk_create_data.append(ke_don_thuoc)

        KeVatTu.objects.bulk_create(bulk_create_data)
        response = {'status': 200, 'message': 'Thống Kê Hoàn Tất'}
    else:
        response = {'status': 404, 'message' : "Có Lỗi Xảy Ra"}
    return HttpResponse(json.dumps(response), content_type='application/json; charset=utf-8')

@login_required(login_url='/dang_nhap/')
def them_vat_tu(request):
    phong_chuc_nang = PhongChucNang.objects.all()
    cong_ty = CongTy.objects.filter(loai_cung = "vat_tu")
    nhom_vat_tu = NhomVatTu.objects.all()
    data = {
        'phong_chuc_nang': phong_chuc_nang,
        'cong_ty'        : cong_ty,
        'nhom_vat_tu'    : nhom_vat_tu,
    }
    return render(request, 'phong_tai_chinh/them_moi_vat_tu.html', context=data)

def create_vat_tu(request):
    if request.method == "POST":
        id_cong_ty        = request.POST.get('id_cong_ty')
        ma_hieu           = request.POST.get('ma_hieu')
        ma_vtyt_bv        = request.POST.get('ma_vtyt_bv')
        quy_cach          = request.POST.get('quy_cach')
        hang_sx           = request.POST.get("hang_san_xuat")
        nuoc_sx           = request.POST.get("nuoc_san_xuat")
        don_vi_tinh       = request.POST.get('don_vi_tinh')
        don_gia           = request.POST.get("don_gia")
        don_gia_tt        = request.POST.get("don_gia_tt")
        id_nhom_vat_tu    = request.POST.get('id_nhom_vat_tu')
        so_luong_kha_dung = request.POST.get("so_luong_kha_dung")
        quyet_dinh        = request.POST.get("quyet_dinh")
        cong_bo           = request.POST.get("cong_bo") 
        ten_vtyt_bv       = request.POST.get('ten_vtyt_bv')   
    
        cong_ty = CongTy.objects.get(id=id_cong_ty)

        nhom_vat_tu = NhomVatTu.objects.get(id = id_nhom_vat_tu)

        VatTu.objects.create(
            nha_thau           = cong_ty,
            don_vi_tinh        = don_vi_tinh,
            don_gia            = don_gia,
            don_gia_tt         = don_gia_tt,
            so_luong_kha_dung  = so_luong_kha_dung,
            hang_sx            = hang_sx,
            nuoc_sx            = nuoc_sx,
            quyet_dinh         = quyet_dinh,
            cong_bo            = cong_bo,
            ma_hieu            = ma_hieu,
            ma_vtyt_bv         = ma_vtyt_bv,
            quy_cach           = quy_cach,
            nhom_vat_tu        = nhom_vat_tu,
            ten_vtyt_bv        = ten_vtyt_bv,
        )

        response = {
            'status' : 200,
            'message' : 'Tạo Thành Công'
        }
        return HttpResponse(json.dumps(response), content_type='application/json; charset=utf-8')

@login_required(login_url='/dang_nhap/')
def update_phong_kham(request, **kwargs):
    id = kwargs.get('id')
    instance = get_object_or_404(PhongKham, id=id)
    form = PhongKhamForm(request.POST or None, instance=instance)
    phong_chuc_nang = PhongChucNang.objects.all()

    data = {
        'form': form,
        'id': id,
        'phong_chuc_nang' : phong_chuc_nang,
    }
    return render(request, 'update_phong_kham.html', context=data)

def store_update_phong_kham(request):
    if request.method == "POST":
        id                  = request.POST.get('id')
        ten_phong_kham      = request.POST.get('ten_phong_kham')
        so_dien_thoai       = request.POST.get('so_dien_thoai')
        email               = request.POST.get('email')
        gia_tri_diem_tich   = request.POST.get('gia_tri_diem_tich')
        chu_khoan           = request.POST.get('chu_khoan')
        so_tai_khoan        = request.POST.get('so_tai_khoan')
        thong_tin_ngan_hang = request.POST.get('thong_tin_ngan_hang')

        phong_kham = get_object_or_404(PhongKham, id=id)
        phong_kham.ten_phong_kham      = ten_phong_kham
        phong_kham.so_dien_thoai       = so_dien_thoai
        phong_kham.email               = email
        phong_kham.gia_tri_diem_tich   = gia_tri_diem_tich
        phong_kham.chu_khoan           = chu_khoan
        phong_kham.so_tai_khoan        = so_tai_khoan
        phong_kham.thong_tin_ngan_hang = thong_tin_ngan_hang
        phong_kham.save()

        response = {
            'status': 200,
            'message': 'Cập Nhật Thông Tin Thành Công'
        }
        return HttpResponse(json.dumps(response), content_type="application/json, charset=utf-8")

@login_required(login_url='/dang_nhap/')
def hoa_don_dich_vu_bao_hiem(request, *args, **kwargs):
    id = kwargs.get('id')
    # chuoi_kham = ChuoiKham.objects.filter(benh_nhan__id=user_id, trang_thai__id = 4)[0]
    chuoi_kham = ChuoiKham.objects.get(id=id)
    hoa_don_dich_vu = chuoi_kham.hoa_don_dich_vu
    danh_sach_phan_khoa = chuoi_kham.phan_khoa_kham.filter(bao_hiem = True)
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
    phong_chuc_nang = PhongChucNang.objects.all()
    phong_kham = PhongKham.objects.all().first()
    data = {
        'chuoi_kham'         : chuoi_kham,
        'tong_tien'          : total_spent,
        'phong_chuc_nang'    : phong_chuc_nang,
        'danh_sach_phan_khoa': danh_sach_phan_khoa,
        'tong_tien'          : total_spent,
        'ap_dung_bao_hiem'   : tong_bao_hiem,
        'thanh_tien'         : thanh_tien,
        'hoa_don_dich_vu'    : hoa_don_dich_vu,
        'phong_kham'         : phong_kham,
    }
    return render(request, 'phong_tai_chinh/hoa_don_dich_vu_bao_hiem.html', context=data)

@login_required(login_url='/dang_nhap/')
def hoa_don_thuoc_bao_hiem(request, **kwargs):
    id = kwargs.get('id')
    don_thuoc = DonThuoc.objects.get(id = id)
    danh_sach_thuoc = don_thuoc.ke_don.filter(bao_hiem=True)
    # tong_tien = []
    # for thuoc_instance in danh_sach_thuoc:
    #     gia = int(thuoc_instance.thuoc.don_gia_tt) * thuoc_instance.so_luong
    #     tong_tien.append(gia)
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
    
    total_spent = sum(tong_tien)
    tong_tien.clear()
    bao_hiem.clear()
    
    phong_chuc_nang = PhongChucNang.objects.all()
    phong_kham = PhongKham.objects.all().first()

    data = {
        'danh_sach_thuoc': danh_sach_thuoc,
        'tong_tien'      : total_spent,
        'don_thuoc'      : don_thuoc,
        'phong_chuc_nang': phong_chuc_nang,
        'thanh_tien'     : thanh_tien,
        'tong_bao_hiem'  : tong_bao_hiem,
        'phong_kham'     : phong_kham,
    }
    return render(request, 'phong_tai_chinh/hoa_don_thuoc_bao_hiem.html', context=data)

# END
