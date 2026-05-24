from django.db import models


class User(models.Model):
    """
    Mirror of FastAPI's users table.
    managed=False means Django reads this table but never creates or drops it.
    FastAPI + Alembic own the schema.
    """
    ROLE_CHOICES = [("candidate", "Candidate"), ("employer", "Employer"), ("admin", "Admin")]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    hashed_password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="candidate")
    company_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "users"
        managed = False
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.full_name} ({self.role})"


class Job(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("closed", "Closed"), ("draft", "Draft")]
    TYPE_CHOICES = [
        ("full_time", "Full Time"), ("part_time", "Part Time"),
        ("contract", "Contract"), ("internship", "Internship"), ("remote", "Remote"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    skills_required = models.CharField(max_length=1000)
    location = models.CharField(max_length=255)
    salary_min = models.FloatField(null=True, blank=True)
    salary_max = models.FloatField(null=True, blank=True)
    job_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="full_time")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    employer = models.ForeignKey(User, on_delete=models.CASCADE, db_column="employer_id")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "jobs"
        managed = False
        verbose_name = "Job"
        verbose_name_plural = "Jobs"

    def __str__(self):
        return f"{self.title} — {self.location}"


class Application(models.Model):
    STATUS_CHOICES = [
        ("applied", "Applied"), ("screening", "Screening"), ("interview", "Interview"),
        ("offered", "Offered"), ("rejected", "Rejected"), ("withdrawn", "Withdrawn"),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    resume_path = models.CharField(max_length=500)
    cover_letter = models.TextField(blank=True, null=True)
    ats_score = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="applied")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "applications"
        managed = False
        verbose_name = "Application"
        verbose_name_plural = "Applications"

    def __str__(self):
        return f"#{self.id} — {self.candidate} → {self.job}"