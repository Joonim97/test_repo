from . import views
from django.urls import path
from .views import (SignupAPIView, VerifyEmailAPIView, LogoutAPIView, SubscribeView, Mypage, PasswordResetRequestView,
                    PasswordResetConfirmView, EmailResetRequestView,
                    EamilResetConfirmView, MyJournalsListAPIView, SavedLocationsListAPIView, 
                    LikeJournalsListAPIView, SubscribingsListAPIView, SubsribingsjournalAPI, MyCommunityListAPIView, DeleteAPIView)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'accounts'

urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="signup"), # 회원가입
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("<str:nickname>/subscribes/", SubscribeView.as_view(), name="subscribes"), # 구독
    path('verify/<str:token>/', VerifyEmailAPIView.as_view(), name='verify_email'), # 회원가입 이메일 인증, 이 path 없으면 이메일 인증시 Not Found 에러 발생
    path('passwordreset/', PasswordResetRequestView.as_view(), name='password_reset'), # 비밀번호 초기화
    path('passwordchange/verify/<str:token>/', PasswordResetConfirmView.as_view(), name='verify_email'), # 비밀번호 변경 이메일 인증
    path('emailreset/', EmailResetRequestView.as_view(), name='email_reset'), # 이메일 초기화
    path('emailchange/verify/<str:token>/', EamilResetConfirmView.as_view(), name='verify_email'), # 이메일변경 이메일 인증
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutAPIView.as_view(), name="logout"), # 로그아웃
    path("<str:nickname>/mypage/", Mypage.as_view(), name="mypage"), # 마이페이지
    path('<str:nickname>/mypage/journallike/', LikeJournalsListAPIView.as_view(), name='journal_like'), # 내가 좋아요한 저널 글 목록
    path('<str:nickname>/mypage/myjournals/', MyJournalsListAPIView.as_view(), name='my_journals'), # 내가 쓴 글 전체보기
    path('<str:nickname>/mypage/savedlocations/', SavedLocationsListAPIView.as_view(), name='saved_locations'), # 저장한 촬영지 전체보기
    path('<str:nickname>/mypage/subscribings/', SubscribingsListAPIView.as_view(), name='subscribings'), # 내가 구독한 사람 전체보기
    path('<str:nickname>/mypage/communitiesauthor/', MyCommunityListAPIView.as_view(), name='my_journals'), # 내가 쓴 글 전체보기
    path('<str:nickname>/mypage/<str:sub_nickname>/', SubsribingsjournalAPI.as_view(), name='subscribings_journal'), # 내가 구독한 인원 글 보기
    path('<str:nickname>/delete/', DeleteAPIView.as_view(), name='accounts_delete')
]