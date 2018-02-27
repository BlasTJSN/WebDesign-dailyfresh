from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings


class FastDFSStorage(Storage):
    """自定义Django存储系统的类:运维在后台站点上传图片时调用"""

    # 这些方法都继承自Storage类，现在重写为自定义的方法
    def __init__(self, client_conf=None, server_ip=None):
        """初始化，设置参数"""

        if client_conf is None:
            # 使用settings实现解耦
            client_conf = settings.CLIENT_CONF
        self.client_conf = client_conf

        if server_ip is None:
            server_ip = settings.SERVER_IP
        self.server_ip = server_ip

    def _open(self, name, mode="rb"):
        """读取文件时使用：此处只做存储，不打开文件，所以pass"""
        pass

    def _save(self, name, content):
        """存储文件时使用：参数2是上传的文件名，参数3是上传的File对象"""

        # 创建fdfs客户端client
        client = Fdfs_client(self.client_conf)

        # clinet获取文件内容
        file_data = content.read()

        # Django借助client向FastDFS服务器上传文件,接收返回值
        try:
            result = client.upload_by_buffer(file_data)
        except Exception as e:
            print(e)
            raise

        # 根据返回数据，判断是否上传成功
        if result.get("Status") == "Upload successed.":
            # 读取file_id
            file_id = result.get("Remote file_id")
            # 存储file_id:只需要返回file_id,我们的client,会自动的检测当前站点中正在使用的模型类,然后存储进去
            # 如果当前运维在操作GoodsSKU模型类,上传图片,那么return file_id,会自动存储到GoodsSKU模型类对应的数据库表中
            return file_id
        else:
            # 开发工具类时，出现异常不要擅自处理，交给使用者处理
            raise Exception("上传文件到FastDFS失败")

    def exists(self, name):
        """Django用来判断文件是否存在"""

        # 由于Django不存储图片，所以永远返回False,直接保存到FastFDS
        return False

    def url(self, name):
        """用于返回图片在服务器上完整的地址：server_ip+path"""

        # 拼接地址，下载时使用
        return self.server_ip + name

