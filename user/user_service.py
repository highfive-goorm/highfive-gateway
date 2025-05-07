from user.serializers import UserRequestSerializer


def create_user(data, current_user=None):
    serializer = UserRequestSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=current_user)
    return serializer.data
