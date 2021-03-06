from clinic.api import DanhSachHoaDonThuocBaoHiem, DanhSachPhongKham
from collections import namedtuple
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.db.models import base
from django.views.generic import RedirectView
from medicine.api import ThuocViewSet, CongTyViewSet
from os import name
from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from .api import (ChuoiKhamGanNhat, ChuoiKhamNguoiDung, ChuoiKhamViewSet,DangKiAPI, DangKiLichHen, DanhSachBacSi, DanhSachBacSi1, DanhSachBaiDang, DanhSachBenhNhan, DanhSachBenhNhanChoLamSang,DanhSachBenhNhanTheoPhong, DanhSachBenhNhanTheoPhongChucNang,DanhSachChuoiKhamBenhNhan, DanhSachDichVuKhamTheoPhong,DanhSachDichVuTheoPhongChucNang, DanhSachDoanhThuTheoThoiGian,DanhSachDoanhThuDichVu, DanhSachDoanhThuThuoc, DanhSachDonThuocBenhNhan,DanhSachDonThuocDaKe,DanhSachDonThuocPhongThuoc, DanhSachHoaDonDichVu,DanhSachHoaDonThuoc, DanhSachKhamTrongNgay, DanhSachLichHenTheoBenhNhan,DanhSachPhongChucNang, DanhSachVatTu, DanhSachThanhToanLamSang,DanhSachThuocBenhNhan, DanhSachThuocTheoCongTy, DieuPhoiPhongChucNangView,DonThuocGanNhat, FileKetQuaViewSet, KetQuaChuoiKhamBenhNhan,KetQuaChuoiKhamBenhNhan2, LichHenKhamViewSet, ListNguoiDungDangKiKham,PhanKhoaKhamBenhNhan, PhongChucNangTheoDichVu, SetChoThanhToan,SetXacNhanKham, TatCaLichHenBenhNhan, ThongTinBenhNhanTheoMa,ThongTinPhongChucNang, UserInfor, UserViewSet, DichVuKhamViewSet,PhongChucNangViewSet,LichHenKhamSapToi, UserUpdateInfo,UserUpdateInfoRequest, UploadAvatarView,UpdateAppointmentDetail,CapNhatLichHen, HoaDonChuoiKhamNguoiDung, HoaDonChuoiKhamCanThanhToan,HoaDonThuocCanThanhToan, DichVuTheoPhongChucNang, DonThuocCuaChuoiKham, HoaDonThuocCuaChuoiKham, HoaDonDichVuCuaChuoiKham, HoaDonLamSangChuoiKham, HoaDonLamSangGanNhat, DanhSachHoaDonDichVuBaoHiem, DanhSachDoanhThuLamSang)
from .views import BatDauChuoiKhamToggle, KetThucChuoiKhamToggle, LoginView, ThanhToanHoaDonDichVuToggle, add_lich_hen, bat_dau_chuoi_kham, cap_nhat_thong_tin_bac_si, cap_nhat_thong_tin_benh_nhan, cap_nhat_user, chi_tiet_bai_dang, chinh_sua_don_thuoc, chinh_sua_nguon_cung, chinh_sua_phong_chuc_nang, chinh_sua_thuoc, chinh_sua_thuoc_phong_thuoc, create_bac_si, create_dich_vu, create_user, danh_sach_bac_si, danh_sach_bai_dang, danh_sach_benh_nhan, danh_sach_benh_nhan_cho, danh_sach_dich_vu_kham, danh_sach_kham, danh_sach_phong_chuc_nang, danh_sach_thuoc, danh_sach_thuoc_phong_tai_chinh, danh_sach_vat_tu, doanh_thu_phong_kham, don_thuoc, dung_kham, dung_kham_chuyen_khoa, files_upload_view, hoa_don_dich_vu, hoa_don_thuoc, import_dich_vu_excel, import_thuoc_excel, import_vat_tu_excel, index, login, nhan_don_thuoc, phan_khoa_kham, phong_chuyen_khoa, phong_tai_chinh_danh_sach_cho, phong_thuoc_danh_sach_cho, store_cong_ty, store_ke_don, store_phan_khoa, store_thanh_toan_lam_sang, store_update_dich_vu_kham, them_bai_dang, them_dich_vu_kham, them_dich_vu_kham_excel, them_phong_chuc_nang, them_thuoc_excel, them_vat_tu_excel, update_bac_si, update_benh_nhan, update_dich_vu_kham, update_don_thuoc, update_nguon_cung, update_phong_chuc_nang, update_thuoc, update_thuoc_phong_thuoc, update_user, upload_bai_dang, upload_files_chuyen_khoa, upload_files_lam_sang, upload_view, them_moi_thuoc_phong_tai_chinh, create_thuoc, cong_ty, update_lich_hen, danh_sach_lich_hen, store_update_lich_hen, ThanhToanHoaDonThuocToggle, thanh_toan_hoa_don_thuoc, them_thuoc_phong_tai_chinh, upload_view_lam_sang, xoa_dich_vu, xoa_lich_hen, xoa_thuoc, xoa_vat_tu, them_pcn_kem_dich_vu, xoa_lich_hen, xuat_bao_hiem, upload_ket_qua_lam_sang, upload_ket_qua_chuyen_khoa

from medicine.views import ke_don_thuoc_view
from clinic.views import create_vat_tu, hoa_don_dich_vu_bao_hiem, hoa_don_thuoc_bao_hiem, loginUser, store_thong_ke_vat_tu, store_update_phong_kham, them_vat_tu, thong_ke_vat_tu, thong_tin_phong_kham, update_phong_kham

router = routers.DefaultRouter()
router.register('api/nguoi_dung', UserViewSet, basename="users")
router.register('api/dich_vu', DichVuKhamViewSet, basename="dich_vu_kham")
router.register('api/phong_chuc_nang', PhongChucNangViewSet, basename="phong_chuc_nang")
router.register('api/lich_kham', LichHenKhamViewSet, basename="lich_kham")
router.register('api/chuoi_kham', ChuoiKhamViewSet, basename="chuoi_kham")
router.register('api/danh_sach_thuoc', ThuocViewSet, basename="thuoc"),
router.register('api/cong_ty', CongTyViewSet, basename="cong_ty")

# ajax_router = routers.DefaultRouter()
# ajax_router.register('', FileKetQuaViewSet, basename="upload")

nguoi_dung = UserViewSet.as_view(
    {
        'get': 'retrieve',
        'put': 'update',
    }
)

dich_vu = DichVuKhamViewSet.as_view(
    {   
        'post': 'create',
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }
)

them_thuoc = ThuocViewSet.as_view(
    {
        'post': 'create'
    }
)

phong_chuc_nang = PhongChucNangViewSet.as_view(
    {
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }
)

lich_kham = LichHenKhamViewSet.as_view(
    {
        'get': 'retrieve', 
        'put': 'update', 
        'delete': 'destroy'
    }
)

chuoi_kham = ChuoiKhamViewSet.as_view(
    {
        'get': 'retrieve', 
        'put': 'update', 
        'delete': 'destroy'
    }
)

urlpatterns = [
    path('router/', include(router.urls)),

    # * API
    path('router/api/nguoi_dung/<int:pk>/', nguoi_dung, name='nguoi_dung'),
    path('router/router/api/dich_vu/<int:pk>/', dich_vu, name='dich_vu'),
    path('router/api/phong_chuc_nang/<int:pk>/', phong_chuc_nang, name='phong_chuc_nang'),

    path('api/them_thuoc/', create_thuoc, name="them_thuoc_api"),
    # path('api/dieu_phoi/phong_chuc_nang/<int:pk>/', DieuPhoiPhongChucNangView.as_view(), name='dieu_phoi'),
    # path('api/lich_kham<int:pk>/', lich_kham, name='lich_kham'),
    path('api/danh_sach_benh_nhan_cho_lam_sang/', DanhSachBenhNhanChoLamSang.as_view(), name='danh_sach_benh_nhan_cho_lam_sang'),
    path('router/api/chuoi_kham/<int:pk>/', chuoi_kham, name='chuoi_kham'),
    path('api/danh_sach_lich_hen/', ListNguoiDungDangKiKham.as_view(), name='danh_sach_lich_hen'),
    path('api/danh_sach_chuoi_kham/', ChuoiKhamNguoiDung.as_view(), name='danh_sach_chuoi_kham_nguoi_dung'),
    path('api/danh_sach_benh_nhan_theo_phong/', DanhSachBenhNhanTheoPhong.as_view(), name='danh_sach_benh_nhan_theo_phong'),
    path('api/dich_vu_kham/phong_chuc_nang/', PhongChucNangTheoDichVu.as_view(), name='phong_chuc_nang_theo_dich_vu'),
    path('api/thong_tin_phong_chuc_nang/', ThongTinPhongChucNang.as_view(), name='thong_tin_phong_chuc_nang'),
    path('api/danh_sach_phong_chuc_nang/', DanhSachPhongChucNang.as_view(), name='danh_sach_phong_chuc_nang'),
    path('api/danh_sach_dich_vu_theo_phong_chuc_nang/', DanhSachDichVuTheoPhongChucNang.as_view(), name='danh_sach_dich_vu_kham_theo_phong_chuc_nang'),
    path('api/danh_sach_thuoc_theo_cong_ty/', DanhSachThuocTheoCongTy.as_view(), name='danh_sach_thuoc_theo_cong_ty'),
    path('api/danh_sach_dich_vu_kham_theo_phong/', DanhSachDichVuKhamTheoPhong.as_view(), name='danh_sach_dich_vu_kham_theo_phong'),
    path('api/danh_sach_bai_dang/', DanhSachBaiDang.as_view(), name='danh_sach_bai_dang'),
    path('api/ket_qua_chuoi_kham/', KetQuaChuoiKhamBenhNhan.as_view(), name="ket_qua_chuoi_kham"),
    path('api/ket_qua_chuoi_kham_nguoi_dung/', KetQuaChuoiKhamBenhNhan2.as_view(), name="ket_qua_chuoi_kham"),

    # path('upload/', include(ajax_router.urls)),
    path('api/danh_sach_thanh_toan/', DanhSachHoaDonDichVu.as_view(), name='danh_sach_thanh_toan'),
    path('api/danh_sach_hoa_don_thuoc/', DanhSachHoaDonThuoc.as_view(), name='danh_sach_hoa_don_thuoc'),
    path('api/danh_sach_doanh_thu_theo_thoi_gian/', DanhSachDoanhThuTheoThoiGian.as_view(), name='danh_sach_doanh_thu_theo_thoi_gian'),
    path('api/danh_sach_don_thuoc_da_ke/', DanhSachDonThuocDaKe.as_view(), name='danh_sach_don_thuoc_da_ke'),
    path('api/danh_sach_lam_sang/', DanhSachThanhToanLamSang.as_view(), name='danh_sach_lam_sang'),
    path('api/danh_sach_kham_trong_ngay/', DanhSachKhamTrongNgay.as_view(), name='danh_sach_kham_trong_ngay'),
    path('api/thanh_toan_don_thuoc/', ThanhToanHoaDonThuocToggle.as_view(), name='thanh_toan_don_thuoc_api'),
    path('api/danh_sach_don_thuoc_phong_thuoc/', DanhSachDonThuocPhongThuoc.as_view(), name='danh_sach_don_thuoc_phong_thuoc'),
    path('api/thanh_toan_hoa_don_dich_vu/', ThanhToanHoaDonDichVuToggle.as_view(), name='thanh_toan_hoa_don_dich_vu_api'),
    path('api/danh_sach_benh_nhan/', DanhSachBenhNhan.as_view(), name='danh_sach_benh_nhan'),
    path('api/danh_sach_benh_nhan_theo_thoi_gian/', DanhSachLichHenTheoBenhNhan.as_view(), name='danh_sach_benh_nhan_theo_thoi_gian'),
    path('api/thong_tin_benh_nhan_theo_ma/', ThongTinBenhNhanTheoMa.as_view(), name='thong_tin_benh_nhan_thao_ma'),
    path('api/danh_sach_phong_chuc_nang/', DanhSachPhongChucNang.as_view(), name='danh_sach_phong_chuc_nang_api'),

    path('api/benh_nhan/danh_sach_don_thuoc/', DanhSachDonThuocBenhNhan.as_view(), name='danh_sach_don_thuoc_benh_nhan'),
    path('api/benh_nhan/don_thuoc/', DanhSachThuocBenhNhan.as_view(), name='danh_sach_thuoc_benh_nhan'),
    path('api/benh_nhan/tat_ca_lich_hen/', TatCaLichHenBenhNhan.as_view(), name='tat_ca_lich_hen'),
    path('api/benh_nhan/chuoi_kham_gan_nhat/', ChuoiKhamGanNhat.as_view(), name='chuoi_kham_gan_nhat'),
    path('api/benh_nhan/danh_sach_chuoi_kham/', DanhSachChuoiKhamBenhNhan.as_view(), name='danh_sach_chuoi_kham_benh_nhan'),
    path('api/benh_nhan/chuoi_kham/ket_qua/', KetQuaChuoiKhamBenhNhan.as_view(), name='ket_qua_chuoi_kham_benh_nhan'),
    path('api/banh_nhan/dang_ki_lich_hen/', DangKiLichHen.as_view(), name='dang_ki_lich_hen'),
    path('api/benh_nhan/thong_tin/', UserInfor.as_view(), name='thong_tin_benh_nhan'),
    path('api/lich_hen_sap_toi/', LichHenKhamSapToi.as_view(), name='lich_hen_sap_toi_benh_nhan'),

    path('api/danh_sach_bac_si/', DanhSachBacSi.as_view(), name='danh_sach_bac_si'),
    # path('api/danh_sach_dich_vu/', PaginatedDichVuKhamListView.as_view(), name='danh_sach_dich_vu'),
    path('api/danh_sach_bai_dang/', DanhSachBaiDang.as_view(), name='danh_sach_bai_dang'),
    path('api/danh_sach_phong_chuc_nang/', DanhSachPhongChucNang.as_view(), name='danh_sach_phong_chuc_nang'),

    path('api/lich_hen_sap_toi/', LichHenKhamSapToi.as_view(), name='lich_hen_sap_toi'),
    path('api/don_thuoc_gan_nhat/', DonThuocGanNhat.as_view(), name='don_thuoc_gan_nhat'),

    path('api/danh_sach_phan_khoa/', PhanKhoaKhamBenhNhan.as_view(), name='danh_sach_phan_khoa'),
    path('api/benh_nhan/danh_sach_don_thuoc/', DanhSachDonThuocBenhNhan.as_view(), name='danh_sach_don_thuoc_benh_nhan'),
    path('api/benh_nhan/don_thuoc/', DanhSachThuocBenhNhan.as_view(), name='danh_sach_thuoc_benh_nhan'),
    path('api/benh_nhan/tat_ca_lich_hen/', TatCaLichHenBenhNhan.as_view(), name='tat_ca_lich_hen'),
    path('api/benh_nhan/chuoi_kham_gan_nhat/', ChuoiKhamGanNhat.as_view(), name='chuoi_kham_gan_nhat'),
    path('api/benh_nhan/danh_sach_chuoi_kham/', DanhSachChuoiKhamBenhNhan.as_view(), name='danh_sach_chuoi_kham_benh_nhan'),
    path('api/benh_nhan/chuoi_kham/ket_qua/', KetQuaChuoiKhamBenhNhan.as_view(), name='ket_qua_chuoi_kham_benh_nhan'),
    path('api/banh_nhan/dang_ki_lich_hen/', DangKiLichHen.as_view(), name='dang_ki_lich_hen'),
    path('api/benh_nhan/thong_tin/', UserInfor.as_view(), name='thong_tin_benh_nhan'),

    path('api/danh_sach_benh_nhan_theo_phong_chuc_nang/', DanhSachBenhNhanTheoPhongChucNang.as_view(), name="danh_sach_benh_nhan_theo_phong_chuc_nang"),
    path('api/bat_dau_chuoi_kham/', BatDauChuoiKhamToggle.as_view(), name='bat_dau_chuoi_kham_api'),
    path('api/ket_thuc_chuoi_kham/', KetThucChuoiKhamToggle.as_view(), name='ket_thuc_chuoi_kham_api'),
    path('api/danh_sach_doanh_thu_dich_vu/', DanhSachDoanhThuDichVu.as_view(), name='danh_sach_doanh_thu_dich_vu'),
    path('api/danh_sach_doanh_thu_thuoc/', DanhSachDoanhThuThuoc.as_view(), name='danh_sach_daonh_thu_thuoc'),
    # * VIEW
    path('', RedirectView.as_view(url='trang_chu/'), name='index'),
    path('trang_chu/', index, name='index'),
    path('danh_sach_benh_nhan/', danh_sach_benh_nhan, name='danh_sach_benh_nhan'),
    path('danh_sach_benh_nhan/<int:id>/cap_nhat_thong_tin_benh_nhan', update_benh_nhan, name="update_benh_nhan"),
    path('cap_nhat_thong_tin_benh_nhan/', cap_nhat_thong_tin_benh_nhan, name="cap_nhat_thong_tin_benh_nhan"),
    
    path('bac_si_lam_sang/danh_sach_benh_nhan_cho/', danh_sach_benh_nhan_cho, name='danh_sach_benh_nhan_cho'),
    path('dang_nhap/', LoginView.as_view(), name='dang_nhap'),
    path('dang_ki/', create_user, name="dang_ki_nguoi_dung"),
    path('phong_chuyen_khoa/<int:id_phong_chuc_nang>', phong_chuyen_khoa, name='phong_chuyen_khoa'),
    path('phong_chuyen_khoa/<int:id_phong_chuc_nang>/benh_nhan/<int:id>/upload/', upload_view, name='upload_ket_qua_chuyen_khoa'),
    path('danh_sach_benh_nhan_cho/phan_khoa_kham/<int:id_lich_hen>/', phan_khoa_kham, name='phan_khoa_kham'),
    path('bac_si_lam_sang/ket_qua_kham/', danh_sach_kham, name='danh_sach_kham'),
    path('bac_si_lam_sang/benh_nhan/<int:id>/upload/', upload_view_lam_sang, name='upload_ket_qua_lam_sang'),
    path('danh_sach_kham/ke_don_thuoc/<int:user_id>/<int:id_chuoi_kham>/', ke_don_thuoc_view, name='ke_don_thuoc'),

    # path('test/', testView, name="test"),
    path('store_phan_khoa_kham/', store_phan_khoa, name='store_phan_khoa'),
    path('store_ke_don/', store_ke_don, name='store_ke_don'),
    path('chinh_sua_ke_don/', chinh_sua_don_thuoc, name='chinh_sua_don_thuoc'),
    path('ke_don_thuoc/', ke_don_thuoc_view, name='ke_don_thuoc'),
    path('upload_files/', files_upload_view, name='upload_files'),
    # path('upload/<int:id>/', upload_view, name='upload'),
    path('upload_files_chuyen_khoa/', upload_files_chuyen_khoa, name="upload_files_chuyen_khoa"),
    path('upload_files_lam_sang/', upload_files_lam_sang, name='upload_files_lam_sang'),
    path('store_cong_ty/', store_cong_ty, name='store_cong_ty'),

    path('danh_sach_lich_hen/', danh_sach_lich_hen, name='danh_sach_lich_hen'),
    path('danh_sach_lich_hen/lich_hen/<int:id>/', update_lich_hen, name='update_lich_hen'),
    path('store_update_lich_hen', store_update_lich_hen, name="store_update_lich_hen"),
    path('xoa_lich_hen/', xoa_lich_hen, name="xoa_lich_hen"),
    path('set_cho_thanh_toan/', SetChoThanhToan.as_view(), name="set_cho_thanh_toan"),
    path('set_xac_nhan_kham/', SetXacNhanKham.as_view(), name="set_xac_nhan_kham"),

    path('bat_dau_chuoi_kham/<int:id>/', bat_dau_chuoi_kham, name='bat_dau_chuoi_kham'),
    path('bac_si_lam_sang/dung_kham_dot_xuat/', dung_kham, name='dung_kham'),
    path('bac_si_chuyen_khoa/dung_kham/', dung_kham_chuyen_khoa, name='dung_kham_chuyen_khoa'),

# ---- MINH UPdate -----
# * -------------------- Update -----------------------
    path('api/thong_tin_chinh_sua/', UserUpdateInfo.as_view(), name='thong_tin_chinh_sua'),
    path('api/chinh_sua_thong_tin/', UserUpdateInfoRequest.as_view(), name='chinh_sua_thong_tin'),
    path('api/chinh_sua_avatar/', UploadAvatarView.as_view(), name='chinh_sua_avatar'),
    path('api/thong_tin_lich_hen/', UpdateAppointmentDetail.as_view(), name='thong_tin_lich_hen'), 
    path('api/chinh_sua_lich_hen/', CapNhatLichHen.as_view(), name='chinh_sua_lich_hen'),
    path('api/hoa_don_chuoi_kham_can_thanh_toan/', HoaDonChuoiKhamCanThanhToan.as_view(), name='hoa_don_chuoi_kham_can_thanh_toan'), 
    path('api/hoa_don_thuoc_can_thanh_toan/', HoaDonThuocCanThanhToan.as_view(), name='hoa_don_thuoc_can_thanh_toan'),

# * update them 
    path('api/danh_sach_dich_vu/phong_chuc_nang/', DichVuTheoPhongChucNang.as_view(), name='phong_chuc_nang_dich_vu'),

#* update 25-12
    path('api/don_thuoc/chuoi_kham/', DonThuocCuaChuoiKham.as_view(), name='don_thuoc_cua_chuoi_kham'),
    path('api/hoa_don_dich_vu/chuoi_kham/', HoaDonDichVuCuaChuoiKham.as_view(), name='hoa_don_dich_vu_cua_chuoi_kham'),
    path('api/hoa_don_thuoc/chuoi_kham/', HoaDonThuocCuaChuoiKham.as_view(), name='hoa_don_thuoc_cua_chuoi_kham'),
    path('api/hoa_don_lam_sang/', HoaDonLamSangChuoiKham.as_view(), name='hoa_don_lam_sang'),
    path('api/hoa_don_lam_sang_gan_nhat/', HoaDonLamSangGanNhat.as_view(), name='hoa_don_lam_sang_gan_nhat'),



    path('phong_tai_chinh/', phong_tai_chinh_danh_sach_cho, name='phong_tai_chinh'),
    path('phong_thuoc/', phong_thuoc_danh_sach_cho, name='phong_thuoc'),
    path('phong_tai_chinh/hoa_don_dich_vu/<int:id_chuoi_kham>/', hoa_don_dich_vu, name='hoa_don_dich_vu'),
    path('phong_tai_chinh/hoa_don_thuoc/<int:id_don_thuoc>/', hoa_don_thuoc, name='hoa_don_thuoc'),
    path('phong_tai_chinh/danh_sach_thuoc/', danh_sach_thuoc_phong_tai_chinh, name='danh_sach_thuoc_phong_tai_chinh'),
    path('phong_tai_chinh/hoa_don_thuoc/thanh_toan/', thanh_toan_hoa_don_thuoc, name='thanh_toan_hoa_don_thuoc'),
    path('phong_tai_chinh/them_thuoc/', them_thuoc_phong_tai_chinh, name='them_thuoc_phong_tai_chinh'),
    path('phong_thuoc/don_thuoc/<int:id_don_thuoc>/', don_thuoc, name='don_thuoc'),
    path('phong_thuoc/danh_sach_thuoc/', danh_sach_thuoc, name='danh_sach_thuoc_phong_thuoc'),
    path('phong_tai_chinh/them_moi_thuoc/', them_moi_thuoc_phong_tai_chinh, name="phong_tai_chinh_them_moi_thuoc"),
    path('phong_tai_chinh/danh_sach_vat_tu/', danh_sach_vat_tu, name='danh_sach_vat_tu'),
    path('phong_tai_chinh/them_vat_tu_excel/', them_vat_tu_excel, name='them_vat_tu_excel'),
    path('store_vat_tu_excel/', import_vat_tu_excel, name="import_vat_tu_excel"),
    path('store_dich_vu_kham/', create_dich_vu, name="store_dich_vu_kham"),
    path('nguon_cung/', cong_ty, name="nguon_cung"),
    path('nguon_cung/<int:id>/chinh_sua/', update_nguon_cung, name="update_nguon_cung"),
    path('chinh_sua/', chinh_sua_nguon_cung, name="chinh_sua"),
    path('danh_sach_phong_chuc_nang/', danh_sach_phong_chuc_nang, name="danh_sach_phong_chuc_nang"),
    path('them_phong_chuc_nang/', them_phong_chuc_nang, name="them_phong_chuc_nang"),
    path('danh_sach_dich_vu_kham/', danh_sach_dich_vu_kham, name="danh_sach_dich_vu_kham"),
    # path('danh_sach_phong_chuc_nang/<int:id>/chinh_sua_phong_chuc_nang', update_phong_chuc_nang, name="update_phong_chuc_nang"),
    path('danh_sach_dich_vu_kham/<int:id>/chinh_sua_dich_vu_kham', update_dich_vu_kham, name="update_dich_vu_kham"),
    path('chinh_sua_phong_chuc_nang/', chinh_sua_phong_chuc_nang, name="chinh_sua_phong_chuc_nang"),
    path('cap_nhat_thong_tin/<int:id>', update_user, name="update_user"),
    path('cap_nhat_user/', cap_nhat_user, name="cap_nhat_user"),
    path('phong_tai_chinh/danh_sach_thuoc/<str:id_thuoc>/cap_nhat_thuoc/', chinh_sua_thuoc, name="cap_nhat_thuoc"),
    path('update_thuoc/', update_thuoc, name="update_thuoc"),
    path('phong_thuoc/danh_sach_thuoc/<str:id_thuoc>/cap_nhat_thuoc/', chinh_sua_thuoc_phong_thuoc, name="cap_nhat_thuoc_phong_thuoc"),
    path('update_thuoc_phong_thuoc/', update_thuoc_phong_thuoc, name="update_thuoc_phong_thuoc"),
    path('phong_tai_chinh/doanh_thu_phong_kham/', doanh_thu_phong_kham, name="doanh_thu_phong_kham"),
    path('them_dich_vu_kham_excel/', them_dich_vu_kham_excel, name='them_dich_vu_kham_excel'),
    path('store_dich_vu_excel/', import_dich_vu_excel, name="import_dich_vu_excel"),
    path('them_thuoc_excel/', them_thuoc_excel, name="them_thuoc_excel"),
    path('import_thuoc_excel/', import_thuoc_excel, name="import_thuoc_excel"),
    path('them_dich_vu_kham/', them_dich_vu_kham, name="them_dich_vu_kham"),
    path('tao_lich_hen/', add_lich_hen, name='add_lich_hen'),
    path('danh_sach_bai_dang/', danh_sach_bai_dang, name="danh_sach_bai_dang"),
    path('thanh_toan_lam_sang/', store_thanh_toan_lam_sang, name="store_thanh_toan_lam_sang"),
    path('don_thuoc/chinh_sua/<int:id>/', update_don_thuoc, name="update_don_thuoc"),
    path('nhan_don_thuoc/', nhan_don_thuoc, name="nhan_don_thuoc"),
 
    path('them_pcn_kem_dich_vu/', them_pcn_kem_dich_vu, name='them_pcn_kem_dich_vu'),
    path('them_bai_dang/', them_bai_dang, name="them_bai_dang"),
    path('upload_bai_dang/', upload_bai_dang, name="upload_bai_dang"),
    path('bai_dang/<int:id>/', chi_tiet_bai_dang, name="chi_tiet_bai_dang"),
    
    path('xoa_thuoc/', xoa_thuoc, name="xoa_thuoc"),
    path('xoa_dich_vu/', xoa_dich_vu, name="xoa_dich_vu"),
    path('store_update_dich_vu_kham/', store_update_dich_vu_kham, name="store_update_dich_vu_kham"),
    path('api/danh_sach_vat_tu/', DanhSachVatTu.as_view(), name="api_danh_sach_vat_tu"),
    path('xoa_vat_tu/', xoa_vat_tu, name="xoa_vat_tu"),
    

    path('login/', login, name='login'),
    path('loginUser/', loginUser, name='loginUser'),
    
    path('logout/',auth_views.LogoutView.as_view(next_page='login'),name='logout'),
    
    # UPDATE BY LONG
    path('danh_sach_bac_si/', danh_sach_bac_si, name="view_danh_sach_bac_si"),
    path('create_bac_si/', create_bac_si, name="create_bac_si"),
    path('api/danh_sach_bac_si_api/', DanhSachBacSi1.as_view(), name="danh_sach_bac_si_api"),
    path('danh_sach_bac_si/<int:id>/<int:user_id>/cap_nhat_thong_tin/', update_bac_si, name="update_bac_si"),
    path('cap_nhat_thong_tin_bac_si/', cap_nhat_thong_tin_bac_si, name="cap_nhat_thong_tin_bac_si"),
    # END
    
    # UPDATE NGAY 3/1
    path('xoa_lich_hen/', xoa_lich_hen, name="xoa_lich_hen"), 
    path('phong_tai_chinh/xuat_bao_hiem/', xuat_bao_hiem, name="xuat_bao_hiem"), 
    path('api/danh_sach_hoa_don_dich_vu_bao_hiem/', DanhSachHoaDonDichVuBaoHiem.as_view(), name="danh_sach_hoa_don_dich_vu_bao_hiem"),
    path('upload_ket_qua_lam_sang/', upload_ket_qua_lam_sang, name="upload_ket_qua_lam_sang"),
    path('upload_ket_qua_chuyen_khoa/', upload_ket_qua_chuyen_khoa, name="upload_ket_qua_chuyen_khoa"),
    path('api/danh_sach_doanh_thu_lam_sang/', DanhSachDoanhThuLamSang.as_view(), name="danh_sach_doanh_thu_lam_sang"), #import DoanhThuLamSang

    # END

    # UPDATE 9/1
    path('thong_tin_phong_kham/', thong_tin_phong_kham, name="thong_tin_phong_kham"),
    path('thong_ke_vat_tu/', thong_ke_vat_tu, name="thong_ke_vat_tu"),
    path('store_thong_ke_vat_tu/', store_thong_ke_vat_tu, name="store_thong_ke_vat_tu"),
    path('phong_tai_chinh/them_vat_tu/', them_vat_tu, name="them_vat_tu"),
    path('create_vat_tu/', create_vat_tu, name="create_vat_tu"),
    path('api/danh_sach_phong_kham/', DanhSachPhongKham.as_view(), name="danh_sach_phong_kham_api"),
    path('cap_nhat_thong_tin_phong_kham/<int:id>', update_phong_kham, name="update_phong_kham"),
    path('store_update_phong_kham/', store_update_phong_kham, name="store_update_phong_kham"),
    path('api/danh_sach_hoa_don_thuoc_bao_hiem/', DanhSachHoaDonThuocBaoHiem.as_view(), name="danh_sach_hoa_don_thuoc_bao_hiem_api"),
    path('xuat_bao_hiem/dich_vu/<int:id>', hoa_don_dich_vu_bao_hiem, name="hoa_don_dich_vu_bao_hiem"),
    path('xuat_bao_hiem/thuoc/<int:id>', hoa_don_thuoc_bao_hiem, name="hoa_don_thuoc_bao_hiem"),
    # END
]