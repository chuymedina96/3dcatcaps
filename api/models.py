from django.db import models
import random
import string

def generate_confirmation_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class CapOrderGroup(models.Model):
    confirmation_code = models.CharField(max_length=12, unique=True, default=generate_confirmation_code)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    contact_info = models.EmailField()
    shipping_address = models.TextField(blank=True, null=True)  # ✅ added this
    created_at = models.DateTimeField(auto_now_add=True)
    is_fulfilled = models.BooleanField(default=False)

    def __str__(self):
        return f"Group {self.confirmation_code} ({self.contact_info})"


class CapOrder(models.Model):
    group = models.ForeignKey('CapOrderGroup', on_delete=models.CASCADE, null=True, blank=True, related_name='orders')
    cat_name = models.CharField(max_length=100)
    team = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    pope_leo = models.BooleanField(default=False)
    le_bubu = models.BooleanField(default=False)
    bust_color = models.CharField(max_length=50, blank=True, null=True)
    font = models.CharField(max_length=100, default='Arial')
    font_color = models.CharField(max_length=50, default='white')
    contact_info = models.CharField(max_length=100, null=True, blank=True)
    shipping_address = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        bust = "None"
        if self.pope_leo:
            bust = "Pope Leo"
        elif self.le_bubu:
            bust = f"Le Bubu ({self.bust_color})"

        group_code = self.group.confirmation_code if self.group else "NoGroup"

        return (
            f"Order for {self.cat_name} in Group #{group_code} "
            f"[Team: {self.team} | Color: {self.color} | Bust: {bust} | Font: {self.font} ({self.font_color})] "
            f"by {self.contact_info} - ${self.price}"
        )


class PinkEditionInterest(models.Model):
    interested = models.BooleanField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{'Yes' if self.interested else 'No'} - {self.email or 'Anonymous'}"
