"""PVE模块序列化器。"""

from rest_framework import serializers
from apps.common.serializers import BaseModelSerializer
from .models import PVEServer, VirtualMachine


class PVEServerListSerializer(BaseModelSerializer):
    """PVE服务器列表序列化器。"""
    
    class Meta:
        model = PVEServer
        fields = [
            'id', 'name', 'host', 'port', 'token_id',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PVEServerDetailSerializer(BaseModelSerializer):
    """PVE服务器详情序列化器。"""
    
    virtual_machines_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PVEServer
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
        extra_kwargs = {
            'token_secret': {'write_only': True},
        }
    
    def get_virtual_machines_count(self, obj):
        """获取虚拟机数量。"""
        return obj.virtual_machines.count()


class PVEServerCreateSerializer(BaseModelSerializer):
    """PVE服务器创建序列化器。"""
    
    class Meta:
        model = PVEServer
        fields = [
            'name', 'host', 'port', 'token_id', 'token_secret',
            'verify_ssl', 'is_active', 'remark'
        ]


class PVEServerUpdateSerializer(BaseModelSerializer):
    """PVE服务器更新序列化器。"""
    
    class Meta:
        model = PVEServer
        fields = [
            'name', 'host', 'port', 'token_id', 'token_secret',
            'verify_ssl', 'is_active', 'remark'
        ]


class PVEServerTestSerializer(serializers.Serializer):
    """测试PVE服务器连接序列化器。"""
    
    pass


class VirtualMachineListSerializer(BaseModelSerializer):
    """虚拟机列表序列化器。"""
    
    server_name = serializers.CharField(source='server.name', read_only=True)
    
    class Meta:
        model = VirtualMachine
        fields = [
            'id', 'server', 'server_name', 'vmid', 'name', 'node',
            'status', 'cpu_cores', 'memory_mb', 'disk_gb',
            'ip_address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class VirtualMachineDetailSerializer(BaseModelSerializer):
    """虚拟机详情序列化器。"""
    
    server_name = serializers.CharField(source='server.name', read_only=True)
    
    class Meta:
        model = VirtualMachine
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']


class VirtualMachineCreateSerializer(serializers.Serializer):
    """虚拟机创建序列化器。"""
    
    server_id = serializers.IntegerField(help_text='PVE服务器ID')
    node = serializers.CharField(help_text='节点名称')
    vmid = serializers.IntegerField(help_text='虚拟机ID（如果不提供则自动分配）', required=False, allow_null=True)
    name = serializers.CharField(max_length=255, help_text='虚拟机名称')
    sockets = serializers.IntegerField(default=1, help_text='CPU Sockets', required=False)
    cores = serializers.IntegerField(default=1, help_text='每Socket核心数', required=False)
    cpu = serializers.CharField(default='x86-64-v2-AES', help_text='CPU类型', required=False)
    memory = serializers.IntegerField(default=512, help_text='内存(MB)', required=False)
    scsihw = serializers.CharField(default='virtio-scsi-single', help_text='SCSI硬件类型', required=False)
    numa = serializers.BooleanField(default=False, help_text='是否启用NUMA', required=False)
    disk_size = serializers.CharField(default='10G', help_text='磁盘大小，如：10G', required=False)
    disk_storage = serializers.CharField(help_text='存储名称', required=False)
    iso_storage = serializers.CharField(required=False, help_text='ISO存储名称（可选，如果不提供则使用disk_storage）')
    network_bridge = serializers.CharField(default='vmbr0', help_text='网络桥接', required=False)
    network_firewall = serializers.BooleanField(default=True, help_text='是否启用防火墙', required=False)
    ostype = serializers.CharField(default='l26', help_text='操作系统类型', required=False)
    iso = serializers.CharField(required=False, help_text='ISO镜像路径（可选）')
    description = serializers.CharField(required=False, allow_blank=True, help_text='描述')
    
    def validate_server_id(self, value):
        """验证服务器ID。"""
        try:
            server = PVEServer.objects.get(id=value, is_active=True)
        except PVEServer.DoesNotExist:
            raise serializers.ValidationError("PVE服务器不存在或未启用")
        return value


class VirtualMachineActionSerializer(serializers.Serializer):
    """虚拟机操作序列化器。"""
    
    action = serializers.ChoiceField(
        choices=['start', 'stop', 'shutdown', 'reboot'],
        help_text='操作类型：start-启动, stop-停止, shutdown-关闭, reboot-重启'
    )


class VirtualMachineHardwareUpdateSerializer(serializers.Serializer):
    """虚拟机硬件更新序列化器。"""
    
    params = serializers.DictField(
        child=serializers.CharField(allow_blank=True),
        allow_empty=False,
        help_text='需要更新的硬件配置参数（键值对）'
    )