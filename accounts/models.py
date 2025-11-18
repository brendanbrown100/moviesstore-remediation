from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


def user_profile_image_path(instance, filename):
	# Files will be uploaded to MEDIA_ROOT/profile_pics/user_<id>/<filename>
	return f'profile_pics/user_{instance.user.id}/{filename}'


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	image = models.ImageField(upload_to=user_profile_image_path, blank=True, null=True)

	def __str__(self):
		return f"{self.user.username} Profile"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)
	else:
		# Ensure profile exists and save
		try:
			instance.profile.save()
		except Exception:
			Profile.objects.get_or_create(user=instance)
