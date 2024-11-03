from django.db import models
from django.utils.text import slugify


class SalaryRangeItem(models.Model):
    salary_range = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.salary_range

class YoeItem(models.Model):
    yoe = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.yoe
    
class LevelItem(models.Model):
    level = models.CharField(max_length=20, null=True, blank=True)
    codename = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.level
    
    def save(self, *args, **kwargs):
        if not self.codename and self.level:
            self.codename = slugify(self.level)
        return super().save(*args, **kwargs)
    
class SkillItem(models.Model):
    skill = models.CharField(max_length=20, null=True, blank=True)
    codename = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.skill
    
    def save(self, *args, **kwargs):
        if not self.codename and self.skill:
            self.codename = slugify(self.skill)
        return super().save(*args, **kwargs)

class JobType(models.Model):
    job_type = models.CharField(max_length=30, null=True, blank=True)
    codename = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.job_type
    
    def save(self, *args, **kwargs):
        if not self.codename and self.job_type:
            self.codename = slugify(self.job_type)
        return super().save(*args, **kwargs)
    
class ContractType(models.Model):
    contract_type = models.CharField(max_length=30, null=True, blank=True)
    codename = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.contract_type
    
    def save(self, *args, **kwargs):
        if not self.codename and self.contract_type:
            self.codename = slugify(self.contract_type)
        return super().save(*args, **kwargs)
