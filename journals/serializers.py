from rest_framework import serializers
from .models import Journal


# class CommentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Comment
#         fields = '__all__'
#         read_only_fields = ('article',)

#     def to_representation(self, instance):
#         ret = super().to_representation(instance)
#         ret.pop('article')
#         return ret

class JournalSerializer(serializers.ModelSerializer) :
    # author = serializers.ReadOnlyField(source='author.username')
    # image = serializers.ImageField(use_url=True, required=False)

    class Meta :
        model=Journal
        # fields=['id','title','content','created_at','updated_at']
        fields='__all__'
        read_only_fields = ('id','created_at','updated_at')



class JournalDetailSerializer(JournalSerializer):
    True # 댓글 보이게 추가해야 함