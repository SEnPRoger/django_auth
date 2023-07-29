from rest_framework import serializers
from view.models import View
from post.models import Post
from account.models import Account

class ViewSerializer(serializers.ModelSerializer):
    device = serializers.SerializerMethodField()

    class Meta:
        model = View
        fields = ['post', 'account', 'device']

    def get_device(self):
        request = self.context.get('request')
        if request.user_agent.is_pc:
            return 'pc'
        elif request.user_agent.is_mobile:
            return 'mobile'
        else:
            return 'unknown'
        
    def create(self, validated_data, request):
        # В validated_data будут содержаться все переданные значения для сериализатора
        # Вытащим значения для полей post и account из validated_data
        post = validated_data['post']
        account = validated_data['account']

        # Создаем новую запись о просмотре, используя переданные значения
        view = View.objects.create(
            post=post,
            account=account,
            device=self.get_device()  # Вызываем метод get_device для получения значения device
        )

        return view