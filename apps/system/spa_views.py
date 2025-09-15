from django.http import HttpResponse
from django.views.generic import View
from django.conf import settings
import os

class SPAView(View):
    """
    单页应用(SPA)视图
    处理前端路由，返回index.html让前端路由接管
    """
    
    def get(self, request, *args, **kwargs):
        """
        返回前端的index.html文件
        """
        try:
            # 检查是否为开发环境
            if settings.DEBUG:
                # 开发环境下，重定向到前端开发服务器
                from django.http import HttpResponseRedirect
                frontend_url = f"http://localhost:5173{request.path}"
                return HttpResponseRedirect(frontend_url)
            
            # 生产环境：前端构建文件路径
            frontend_dist_path = os.path.join(settings.BASE_DIR, 'frontend', 'dist')
            index_path = os.path.join(frontend_dist_path, 'index.html')
            
            # 如果index.html存在，返回它
            if os.path.exists(index_path):
                with open(index_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return HttpResponse(content, content_type='text/html')
            else:
                # 如果前端文件不存在，返回简单的HTML页面
                html_content = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>股票分析系统</title>
                    <meta charset="utf-8">
                </head>
                <body>
                    <div id="app">
                        <h1>股票分析系统</h1>
                        <p>前端应用正在加载中...</p>
                        <p>如果您看到此页面，说明前端应用可能还未构建。</p>
                        <p>请运行 <code>npm run build</code> 构建前端应用。</p>
                        <p>开发环境请访问: <a href="http://localhost:5173">http://localhost:5173</a></p>
                    </div>
                </body>
                </html>
                """
                return HttpResponse(html_content, content_type='text/html')
                
        except Exception as e:
            # 出错时返回错误页面
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>错误 - 股票分析系统</title>
                <meta charset="utf-8">
            </head>
            <body>
                <h1>页面加载错误</h1>
                <p>错误信息: {str(e)}</p>
                <p><a href="/api/">返回API文档</a></p>
            </body>
            </html>
            """
            return HttpResponse(error_html, content_type='text/html', status=500)