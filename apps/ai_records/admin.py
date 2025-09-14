from django.contrib import admin
from .models import AIAnalysisRecord, AIModelConfig


@admin.register(AIAnalysisRecord)
class AIAnalysisRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'analysis_type', 'stock_code', 'status', 'created_at']
    list_filter = ['analysis_type', 'status', 'created_at']
    search_fields = ['stock_code', 'prompt']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'analysis_type', 'stock_code', 'status')
        }),
        ('分析内容', {
            'fields': ('prompt', 'result')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AIModelConfig)
class AIModelConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'model_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本配置', {
            'fields': ('name', 'model_name', 'is_active')
        }),
        ('API配置', {
            'fields': ('api_key', 'base_url')
        }),
        ('模型参数', {
            'fields': ('max_tokens', 'temperature')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )