from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import models
from django.db.models import Q
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.views import View, APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Comment, CommentLike, Journal, JournalImage, JournalLike
from .serializers import CommentSerializer, JournalSerializer,JournalDetailSerializer



class JournalListAPIView(ListAPIView): # 저널 전체목록조회, 저널작성, 저널검색
        serializer_class = JournalSerializer
        queryset = Journal.objects.all().order_by('-created_at') # 생성최신순
        parser_classes = (MultiPartParser, FormParser)
        
        def get_queryset(self): # 저널전체목록조회 & 저널검색 | method는 get | 검색어 아무것도 안 넣으면 전체목록 나옴
            permission_classes = [AllowAny]
            queryset = Journal.objects.all().order_by('-created_at')
            search_query= self.request.query_params.get('search', None) # 통합검색 | 'search'라는 파라미터로 검색어를 받음
            title_query= self.request.query_params.get('title',None) # 제목 검색
            content_query= self.request.query_params.get('content',None) # 내용 검색
            author_query= self.request.query_params.get('author',None) # 작성자 검색
            start_date= self.request.query_params.get('start_date', None) # 기간시작일
            end_date= self.request.query_params.get('end_date', None) # 기간종료일
            # 기간입력 예: ?start_date=2023-01-01&end_date=2023-12-31
            
            if search_query:
                queryset=queryset.filter(
                    Q(title__icontains=search_query) | Q(content__icontains=search_query) | Q(author__nickname__icontains=search_query) )
            if title_query :
                queryset=queryset.filter( Q(title__icontains=title_query) )
            if content_query :
                queryset=queryset.filter( Q(content__icontains=content_query) )
            if author_query :
                queryset=queryset.filter( Q(author__nickname__icontains=author_query) )
            
            if start_date:
                start_date_parsed = parse_date(start_date) 
                if start_date_parsed:
                    queryset = queryset.filter(created_at__gte=start_date_parsed)

            if end_date:
                end_date_parsed = parse_date(end_date)
                if end_date_parsed:
                    queryset = queryset.filter(created_at__lte=end_date_parsed)
            return queryset

        def post(self, request): # 작성
            permission_classes = [IsAuthenticated] # 로그인권한
            serializer = JournalSerializer(data=request.data)

            if request.user.grade != 'author' :
                return Response( {"error" : "저널리스트 회원이 아닙니다"}, status=status.HTTP_403_FORBIDDEN)

            if serializer.is_valid(raise_exception=True):
                journal = serializer.save(author=request.user)  # 현재 로그인한 유저 저장
                journal_images = request.FILES.getlist('images')
                for journal_image in journal_images:
                    JournalImage.objects.create(journal=journal, journal_image=journal_image)


                return Response(serializer.data, status=201)
            else:
                return Response(serializer.errors, status=400)


class JournalDetailAPIView(APIView): # 저널 상세조회,수정,삭제
        def get_object(self, pk):
                return get_object_or_404(Journal, pk=pk)

        def get(self, request, pk): # 저널 상세조회
                journal = self.get_object(pk)
                journal.hit() # 저널 조회수 업데이트
                serializer = JournalDetailSerializer(journal)
                return Response(serializer.data)

        def put(self, request, pk):  # 저널 수정
            journal = self.get_object(pk)
            journal_images = request.FILES.getlist('images')
            serializer = JournalDetailSerializer(journal, data=request.data, partial=True)
            
            if journal.author != request.user :
                    return Response( {"error" : "다른 사용자의 글은 수정할 수 없습니다"}, status=status.HTTP_403_FORBIDDEN)

            if serializer.is_valid(raise_exception=True):
                serializer.save()

                # 만약 새로운 이미지가 있다면, 기존 이미지를 삭제하고 새로운 이미지를 추가
                if 'images' in request.FILES or not journal_images:
                    # 기존 이미지 삭제
                    journal.journal_images.all().delete()
                    # 새로운 이미지 저장
                    for journal_image in journal_images:
                        JournalImage.objects.create(journal=journal, journal_image=journal_image)

                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                
        def delete(self, request, pk): # 저널 삭제
                permission_classes = [IsAuthenticated] # 로그인권한
                journal = self.get_object(pk)
                
                if journal.author != request.user :
                    return Response( {"error" : "다른 사용자의 글은 삭제할 수 없습니다"}, status=status.HTTP_403_FORBIDDEN)

                journal.delete()
                return Response({'삭제되었습니다'}, status=status.HTTP_204_NO_CONTENT)     


class JournalLikeAPIView(APIView): # 저널 좋아요/좋아요취소 
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        journal = get_object_or_404(Journal, pk=pk)

        journal_like, created = JournalLike.objects.get_or_create(journal=journal, user=request.user)

        if not created:  # 이미 좋아요를 눌렀다면 취소
            journal_like.delete()
            return Response({"좋아요 취소"}, status=status.HTTP_200_OK)
        return Response({'좋아요 +1'}, status=status.HTTP_200_OK)
    

class CommentView(APIView): # 저널 댓글
    def get(self, request, journal_id):
        comments = Comment.objects.filter(journal_id=journal_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def post(self, request, journal_id, parent_id=None):
        data = request.data.copy()
        journal = get_object_or_404(Journal, id=journal_id)
        data['journal'] = journal_id
        
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
            data['parent'] = parent_comment.id
            
        serializer = CommentSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(journal=journal)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, comment_id): 
        comment = Comment.objects.get(id=comment_id)
        
        if comment.user != request.user:
            raise PermissionDenied("수정 권한이 없습니다.")
        
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, comment_id):
        comment = Comment.objects.get(id=comment_id)
        
        if comment.user != request.user:
            raise PermissionDenied("삭제 권한이 없습니다.")
        
        comment.delete()
        return Response({"댓글이 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)


class CommentLikeView(APIView): # 저널 댓글좋아요
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id, like_type):
        comment = get_object_or_404(Comment, id=comment_id)
        like_instance, created = CommentLike.objects.get_or_create(
            user=request.user,
            comment=comment,
            defaults={'like_type': like_type}
        )
        
        # 이미 좋아요/싫어요가 눌린 상태
        if not created:
            if like_instance.like_type == like_type:
                like_instance.delete()
                message = f'{like_type.capitalize()} 취소'
            else:
                like_instance.like_type = like_type
                like_instance.save()
                message = f'{like_type.capitalize()} 변경됨'
        else:
            message = f'{like_type.capitalize()}!'
        
        # 싫어요가 100개 이상일 경우 댓글 삭제
        dislike_count = CommentLike.objects.filter(comment=comment, like_type='dislike').count()
        if dislike_count >= 100:
            comment.delete()
            return Response({'message': '댓글이 삭제되었습니다.'}, status=status.HTTP_201_CREATED)
        
        return Response({'message': message}, status=status.HTTP_200_OK)
    

class DislikedCommentsView(APIView):
    def get(self, request, min_dislikes):
        # 일정 수 이상의 싫어요를 받은 댓글을 필터링
        disliked_comments = Comment.objects.filter(
            id__in=CommentLike.objects.filter(like_type='dislike')
                                    .values('comment')
                                    .annotate(dislike_count=models.Count('comment'))
                                    .filter(dislike_count__gte=min_dislikes)
                                    .values('comment')
        )

        # 필터링된 댓글을 직렬화
        serializer = CommentSerializer(disliked_comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(login_required, name='dispatch')
class JournalWriteView(View):
    def get(self, request):
        # 저널 작성 페이지로 이동
        return render(request, 'journals/journal_write.html')

    def post(self, request):
        # 저널 작성 로직 처리
        serializer = JournalSerializer(data=request.POST)
        if serializer.is_valid():
            journal = serializer.save(author=request.user)
            # 이미지 파일 처리
            journal_images = request.FILES.getlist('images')
            for journal_image in journal_images:
                JournalImage.objects.create(journal=journal, journal_image=journal_image)

            # 작성 후 저널 상세 페이지로 이동
            return redirect(f'/journals/{journal.id}/detail/')
        else:
            # 유효성 검사 실패 시 다시 작성 페이지로 리다이렉트
            return render(request, 'journals/journal_write.html', {'errors': serializer.errors})