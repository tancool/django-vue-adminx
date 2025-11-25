"""PVE模块视图集。"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db import transaction

from apps.common.viewsets import ActionSerializerMixin
from apps.common.mixins import AuditOwnerPopulateMixin
from .models import PVEServer, VirtualMachine
from .serializers import (
    PVEServerListSerializer,
    PVEServerDetailSerializer,
    PVEServerCreateSerializer,
    PVEServerUpdateSerializer,
    PVEServerTestSerializer,
    VirtualMachineListSerializer,
    VirtualMachineDetailSerializer,
    VirtualMachineCreateSerializer,
    VirtualMachineActionSerializer,
    VirtualMachineHardwareUpdateSerializer,
)
from .pve_client import PVEAPIClient

logger = logging.getLogger(__name__)


class PVEServerViewSet(AuditOwnerPopulateMixin, ActionSerializerMixin, viewsets.ModelViewSet):
    """PVE服务器CRUD视图集。"""
    
    queryset = PVEServer.objects.all().order_by('name')
    
    serializer_class = PVEServerDetailSerializer
    list_serializer_class = PVEServerListSerializer
    retrieve_serializer_class = PVEServerDetailSerializer
    create_serializer_class = PVEServerCreateSerializer
    update_serializer_class = PVEServerUpdateSerializer
    partial_update_serializer_class = PVEServerUpdateSerializer
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'host']
    ordering_fields = ['id', 'name', 'created_at']
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """测试PVE服务器连接。"""
        server = self.get_object()
        
        try:
            client = PVEAPIClient(
                host=server.host,
                port=server.port,
                token_id=server.token_id,
                token_secret=server.token_secret,
                verify_ssl=server.verify_ssl
            )
            
            # 尝试获取版本信息
            version = client.get_version()
            
            return Response({
                'success': True,
                'message': '连接成功',
                'version': version
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': f'连接失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def nodes(self, request, pk=None):
        """获取PVE服务器节点列表。"""
        server = self.get_object()
        
        try:
            client = PVEAPIClient(
                host=server.host,
                port=server.port,
                token_id=server.token_id,
                token_secret=server.token_secret,
                verify_ssl=server.verify_ssl
            )
            
            nodes = client.get_nodes()
            return Response(nodes)
        except Exception as e:
            return Response({
                'detail': f'获取节点列表失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], url_path='nodes/(?P<node>[^/.]+)/vms')
    def node_vms(self, request, pk=None, node=None):
        """获取节点上的虚拟机列表。"""
        server = self.get_object()
        
        try:
            client = PVEAPIClient(
                host=server.host,
                port=server.port,
                token_id=server.token_id,
                token_secret=server.token_secret,
                verify_ssl=server.verify_ssl
            )
            
            vms = client.get_vms(node)
            return Response(vms)
        except Exception as e:
            return Response({
                'detail': f'获取虚拟机列表失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], url_path='nodes/(?P<node>[^/.]+)/storage')
    def node_storage(self, request, pk=None, node=None):
        """获取节点存储列表。"""
        server = self.get_object()
        
        try:
            client = PVEAPIClient(
                host=server.host,
                port=server.port,
                token_id=server.token_id,
                token_secret=server.token_secret,
                verify_ssl=server.verify_ssl
            )
            
            storage = client.get_storage(node)
            return Response(storage)
        except Exception as e:
            return Response({
                'detail': f'获取存储列表失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], url_path='nodes/(?P<node>[^/.]+)/storage/(?P<storage>[^/.]+)/iso')
    def node_storage_iso(self, request, pk=None, node=None, storage=None):
        """获取存储中的ISO镜像列表。"""
        server = self.get_object()
        
        try:
            client = PVEAPIClient(
                host=server.host,
                port=server.port,
                token_id=server.token_id,
                token_secret=server.token_secret,
                verify_ssl=server.verify_ssl
            )
            
            # 获取ISO类型的内容
            content = client.get_storage_content(node, storage, content_type='iso')
            # 过滤出ISO文件
            iso_files = [item for item in content if item.get('content') == 'iso' and item.get('volid', '').endswith('.iso')]
            return Response(iso_files)
        except Exception as e:
            return Response({
                'detail': f'获取ISO镜像列表失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], url_path='nodes/(?P<node>[^/.]+)/network')
    def node_network(self, request, pk=None, node=None):
        """获取节点网络接口列表。"""
        server = self.get_object()
        
        try:
            client = PVEAPIClient(
                host=server.host,
                port=server.port,
                token_id=server.token_id,
                token_secret=server.token_secret,
                verify_ssl=server.verify_ssl
            )
            
            network = client.get_network(node)
            return Response(network)
        except Exception as e:
            return Response({
                'detail': f'获取网络接口失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], url_path='next-vmid')
    def next_vmid(self, request, pk=None):
        """获取下一个可用的VMID。"""
        server = self.get_object()
        
        try:
            client = PVEAPIClient(
                host=server.host,
                port=server.port,
                token_id=server.token_id,
                token_secret=server.token_secret,
                verify_ssl=server.verify_ssl
            )
            
            # 获取下一个VMID
            vmid = client.get_next_vmid()
            return Response({'vmid': vmid})
        except Exception as e:
            return Response({
                'detail': f'获取下一个VMID失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class VirtualMachineViewSet(AuditOwnerPopulateMixin, ActionSerializerMixin, viewsets.ModelViewSet):
    """虚拟机CRUD视图集。"""
    
    queryset = VirtualMachine.objects.all().order_by('-created_at')
    
    serializer_class = VirtualMachineDetailSerializer
    list_serializer_class = VirtualMachineListSerializer
    retrieve_serializer_class = VirtualMachineDetailSerializer
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['server', 'status', 'node']
    search_fields = ['name', 'vmid', 'ip_address']
    ordering_fields = ['id', 'vmid', 'name', 'created_at']
    
    @action(detail=False, methods=['post'])
    def create_vm(self, request):
        """创建虚拟机。"""
        serializer = VirtualMachineCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        server_id = data['server_id']
        node = data['node']
        
        try:
            server = PVEServer.objects.get(id=server_id, is_active=True)
        except PVEServer.DoesNotExist:
            return Response({
                'detail': 'PVE服务器不存在或未启用'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 创建PVE客户端
            client = PVEAPIClient(
                host=server.host,
                port=server.port,
                token_id=server.token_id,
                token_secret=server.token_secret,
                verify_ssl=server.verify_ssl
            )
            
            # 构建虚拟机配置
            vmid = data.get('vmid')
            # 解析磁盘大小（默认10G，最小1G）
            raw_disk_size = data.get('disk_size', '10G') or '10G'
            disk_size_str = str(raw_disk_size).strip()
            disk_size_gb = 10
            try:
                normalized_disk_size = disk_size_str.upper()
                if normalized_disk_size.endswith('G'):
                    disk_size_gb = int(normalized_disk_size.replace('G', '') or 0)
                elif normalized_disk_size.endswith('M'):
                    disk_size_gb = int(normalized_disk_size.replace('M', '') or 0) // 1024
                else:
                    disk_size_gb = int(normalized_disk_size)
            except (ValueError, AttributeError, TypeError):
                logger.warning(f'无法解析磁盘大小 {disk_size_str}，使用默认值10GB')
                disk_size_gb = 10
            if disk_size_gb < 1:
                disk_size_gb = 1
            
            # 构建PVE API参数（使用URL参数，表单格式）
            # PVE API创建虚拟机使用URL参数，所有配置都作为URL参数传递
            params = {
                'vmid': vmid,
                'name': str(data['name']),
                'sockets': int(data.get('sockets', 1)),
                'cores': int(data.get('cores', 1)),
                'cpu': str(data.get('cpu', 'x86-64-v2-AES')),
                'memory': int(data.get('memory', 512)),
                'ostype': str(data.get('ostype', 'l26')),
                'scsihw': str(data.get('scsihw', 'virtio-scsi-single')),
                'numa': 1 if data.get('numa', False) else 0,  # NUMA设置，转换为0或1
            }
            
            # 磁盘配置 - PVE API格式根据存储类型不同
            disk_storage = data.get('disk_storage')
            if disk_storage:
                # 获取存储信息以确定存储类型
                try:
                    storages = client.get_storage(node)
                    storage_info = next((s for s in storages if s.get('storage') == disk_storage), None)
                    storage_type = storage_info.get('type') if storage_info else None
                    
                    # 根据存储类型使用不同的格式
                    if storage_type == 'rbd':
                        # RBD/Ceph存储格式：scsi0=storage:size（数字，无单位）
                        # 例如：ceph:32 表示32GB
                        params['scsi0'] = f'{disk_storage}:{disk_size_gb}'
                        # 可选：添加iothread参数提升性能
                        params['scsi0'] += ',iothread=on'
                    elif storage_type == 'lvm' or storage_type == 'lvmthin':
                        # LVM/LVM-Thin存储格式：scsi0=storage:size（数字，无单位）
                        # 例如：local-lvm:32 表示32GB
                        params['scsi0'] = f'{disk_storage}:{disk_size_gb}'
                    else:
                        # 其他存储类型（如dir, nfs等）使用标准格式：scsi0=storage:size（带单位）
                        params['scsi0'] = f'{disk_storage}:{disk_size_str}'
                except Exception as e:
                    # 如果获取存储信息失败，尝试根据存储名称判断
                    logger.warning(f'获取存储信息失败: {str(e)}')
                    # 如果存储名称包含ceph、rbd、lvm，使用数字格式
                    if 'ceph' in disk_storage.lower() or 'rbd' in disk_storage.lower():
                        params['scsi0'] = f'{disk_storage}:{disk_size_gb},iothread=on'
                    elif 'lvm' in disk_storage.lower():
                        params['scsi0'] = f'{disk_storage}:{disk_size_gb}'
                    else:
                        params['scsi0'] = f'{disk_storage}:{disk_size_str}'
            
            # 网络配置 - PVE API格式：net0=model,bridge=bridge_name,firewall=0|1
            network_bridge = str(data.get('network_bridge', 'vmbr0'))
            network_firewall = 1 if data.get('network_firewall', True) else 0
            params['net0'] = f'virtio,bridge={network_bridge},firewall={network_firewall}'
            
            # ISO配置（如果有）- PVE API格式：ide2=storage:iso/file.iso,media=cdrom
            if data.get('iso'):
                iso_value = str(data['iso'])
                # 如果ISO值是完整路径（如 storage:iso/file.iso），直接使用
                if ':' in iso_value:
                    params['ide2'] = f'{iso_value},media=cdrom'
                else:
                    # 否则使用iso_storage或disk_storage拼接
                    iso_storage = data.get('iso_storage') or disk_storage
                    if iso_storage:
                        params['ide2'] = f'{iso_storage}:iso/{iso_value},media=cdrom'
            
            # 描述（如果有）
            if data.get('description'):
                params['description'] = str(data['description'])
            
            # 记录配置信息用于调试
            logger.info(f'创建虚拟机参数: vmid={vmid}, node={node}, params={params}')
            config_snapshot = params.copy()
            
            # 创建虚拟机 - 传递params作为URL参数
            result = client.create_vm(node, vmid, params)
            
            # 等待任务完成（简化处理，实际应该轮询任务状态）
            # 这里先创建数据库记录
            vm = VirtualMachine.objects.create(
                server=server,
                vmid=vmid,
                name=data['name'],
                node=node,
                status='stopped',
                cpu_cores=data.get('cores', 1),
                memory_mb=data.get('memory', 512),
                disk_gb=disk_size_gb,
                description=data.get('description', ''),
                pve_config=config_snapshot,
                created_by=request.user if request.user.is_authenticated else None,
            )
            
            serializer = VirtualMachineDetailSerializer(vm)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'detail': f'创建虚拟机失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def vm_action(self, request, pk=None):
        """虚拟机操作（启动、停止、重启等）。"""
        vm = self.get_object()
        serializer = VirtualMachineActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action_type = serializer.validated_data['action']
        
        try:
            server = vm.server
            client = PVEAPIClient(
                host=server.host,
                port=server.port,
                token_id=server.token_id,
                token_secret=server.token_secret,
                verify_ssl=server.verify_ssl
            )
            
            if action_type == 'start':
                result = client.start_vm(vm.node, vm.vmid)
                vm.status = 'running'
            elif action_type == 'stop':
                result = client.stop_vm(vm.node, vm.vmid)
                vm.status = 'stopped'
            elif action_type == 'shutdown':
                result = client.shutdown_vm(vm.node, vm.vmid)
                vm.status = 'stopped'
            elif action_type == 'reboot':
                result = client.reboot_vm(vm.node, vm.vmid)
                vm.status = 'running'
            else:
                return Response({
                    'detail': f'不支持的操作: {action_type}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            vm.save()
            
            return Response({
                'success': True,
                'message': f'操作 {action_type} 已提交',
                'upid': result
            })
            
        except Exception as e:
            return Response({
                'detail': f'操作失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='update-hardware')
    def update_hardware(self, request, pk=None):
        """更新虚拟机硬件配置。"""
        vm = self.get_object()
        serializer = VirtualMachineHardwareUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data.get('params', {})
        
        if not params:
            return Response({
                'detail': '缺少需要更新的配置参数'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            server = vm.server
            client = PVEAPIClient(
                host=server.host,
                port=server.port,
                token_id=server.token_id,
                token_secret=server.token_secret,
                verify_ssl=server.verify_ssl
            )
            
            result = client.update_vm_config(vm.node, vm.vmid, params)
            
            # 更新数据库中的缓存配置
            config = client.get_vm_config(vm.node, vm.vmid)
            vm.pve_config = config
            if 'cores' in config and 'sockets' in config:
                vm.cpu_cores = config['cores'] * config['sockets']
            elif 'cores' in config:
                vm.cpu_cores = config['cores']
            if 'memory' in config:
                vm.memory_mb = config['memory']
            vm.save()
            
            return Response({
                'success': True,
                'message': '硬件配置更新已提交',
                'upid': result,
                'config': config
            })
        except Exception as e:
            logger.exception('更新虚拟机硬件配置失败')
            return Response({
                'detail': f'更新虚拟机硬件配置失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def sync_status(self, request, pk=None):
        """同步虚拟机状态。"""
        vm = self.get_object()
        
        try:
            server = vm.server
            client = PVEAPIClient(
                host=server.host,
                port=server.port,
                token_id=server.token_id,
                token_secret=server.token_secret,
                verify_ssl=server.verify_ssl
            )
            
            # 获取虚拟机状态
            status_info = client.get_vm_status(vm.node, vm.vmid)
            config = client.get_vm_config(vm.node, vm.vmid)
            
            # 更新状态
            qmpstatus = status_info.get('status', 'unknown')
            if qmpstatus == 'running':
                vm.status = 'running'
            elif qmpstatus == 'stopped':
                vm.status = 'stopped'
            else:
                vm.status = 'unknown'
            
            # 更新配置信息
            vm.pve_config = config
            if 'cores' in config:
                vm.cpu_cores = config['cores']
            if 'memory' in config:
                vm.memory_mb = config['memory']
            
            vm.save()
            
            serializer = VirtualMachineDetailSerializer(vm)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({
                'detail': f'同步状态失败: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
