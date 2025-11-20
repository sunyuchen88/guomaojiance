import hashlib
import time
import random
import string
import requests
import json
from typing import Dict, Any, Optional
from urllib.parse import urljoin


class QualityInspectionAPI:
    def __init__(self, base_url: str, app_id: str, key: str, debug: bool = False):
        """
        初始化质检API客户端
        
        :param base_url: API基础URL
        :param app_id: 应用ID
        :param key: 签名密钥
        :param debug: 是否开启调试模式
        """
        self.base_url = base_url.rstrip('/')
        self.app_id = app_id
        self.key = key
        self.debug = debug
        
    def _generate_random_string(self, length: int = 5) -> str:
        """生成指定长度的随机字符串"""
        return ''.join(random.choices(string.ascii_lowercase, k=length))
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        生成签名
        
        签名规则：
        1. 将以下字段按字典序升序排列：app_id, time, random_str
        2. 拼接成字符串（使用&连接）：app_id&time&random_str
        3. 拼接key（密钥）：app_id&time&random_str&key
        4. 使用MD5对拼接后的字符串进行加密，生成32位小写签名
        """
        # 按照文档说明，只使用app_id, time, random_str三个字段参与签名计算
        sign_params = {
            'app_id': params['app_id'],
            'time': params['time'],
            'random_str': params['random_str']
        }
        
        # 按照字段名字典序升序排列
        sorted_keys = sorted(sign_params.keys())
        
        # 连接参数值
        sign_values = []
        for k in sorted_keys:
            sign_values.append(str(sign_params[k]))
        
        sign_str = '&'.join(sign_values) + f"&{self.key}"
        
        # 调试信息
        if self.debug:
            print(f"签名字段排序: {sorted_keys}")
            print(f"签名字符串: {sign_str}")
            
        # 生成MD5签名（32位小写）
        signature = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
        
        if self.debug:
            print(f"生成的签名: {signature}")
            
        return signature
    
    def _prepare_request_params(self, biz_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备请求参数
        
        :param biz_data: 业务数据
        :return: 完整的请求参数
        """
        params = {
            'app_id': self.app_id,
            'time': int(time.time()),
            'random_str': self._generate_random_string(),
            'biz': json.dumps(biz_data, ensure_ascii=False)
        }
        
        # 生成签名（注意：biz字段不参与签名计算）
        params['sign'] = self._generate_signature(params)
        
        if self.debug:
            print("完整请求参数:")
            for k, v in params.items():
                print(f"  {k}: {v}")
                
        return params
    
    def get_pending_samples(self, start_time: str, end_time: str, limit: int = 50) -> Dict[str, Any]:
        """
        接口1: 读取待检测样品
        
        :param start_time: 开始时间，格式 "YYYY-MM-DD HH:MM:SS"
        :param end_time: 结束时间，格式 "YYYY-MM-DD HH:MM:SS"
        :param limit: 获取数据量，默认50条
        :return: API响应结果
        """
        endpoint = "/admin/api/test/check/data"
        url = urljoin(self.base_url, endpoint)
        
        # 准备业务数据
        biz_data = {
            "start_time": start_time,
            "end_time": end_time,
            "limit": limit
        }
        
        # 准备完整请求参数
        params = self._prepare_request_params(biz_data)
        
        try:
            response = requests.post(
                url,
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
            )
            return response.json()
        except Exception as e:
            return {"status": 500, "message": f"请求异常: {str(e)}"}
    
    def submit_inspection_results(self, check_no_join: str, check_num: int, goods: list) -> Dict[str, Any]:
        """
        接口2: 检测结果接收
        
        :param check_no_join: 质检编号组合
        :param check_num: 样品数量
        :param goods: 样品数组
        :return: API响应结果
        """
        endpoint = "/admin/api/test/check/feedback"
        url = urljoin(self.base_url, endpoint)
        
        # 准备业务数据
        biz_data = {
            "check_no_join": check_no_join,
            "check_num": check_num,
            "goods": goods
        }
        
        # 准备完整请求参数
        params = self._prepare_request_params(biz_data)
        
        try:
            response = requests.post(
                url,
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
            )
            return response.json()
        except Exception as e:
            return {"status": 500, "message": f"请求异常: {str(e)}"}


def example_1_get_pending_samples():
    """示例1: 调用读取待检测样品接口"""
    print("=== 示例1: 调用读取待检测样品接口 ===")
    
    # 初始化API客户端（开启调试模式）
    api = QualityInspectionAPI(
        base_url="https://test1.yunxianpei.com",
        app_id="689_abc",
        key="67868790",
        debug=True
    )
    
    # 调用接口
    result = api.get_pending_samples(
        start_time="2025-01-01 15:00:00",
        end_time="2025-11-20 15:00:00",
        limit=50
    )
    
    print("请求结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def example_2_submit_inspection_results():
    """示例2: 调用检测结果接收接口"""
    print("\n=== 示例2: 调用检测结果接收接口 ===")
    
    # 初始化API客户端（关闭调试模式以减少输出）
    api = QualityInspectionAPI(
        base_url="https://test1.yunxianpei.com",
        app_id="689_abc",
        key="67868790",
        debug=False
    )
    
    # 准备样品数据
    goods_data = [
        {
            "check_no": "CN20250713001",
            "check_time": "2025-08-31 15:14:22",
            "check_result_url": "https://cti-qts-20190115.obs.cn-north-4.myhuaweicloud.com/detection_report/sample.pdf",
            "check_result": "合格",
            "item": [
                {
                    "item_id": 14,
                    "item_name": "吊白块",
                    "item_res": "不合格",
                    "item_indicator": "阴性"
                },
                {
                    "item_id": 15,
                    "item_name": "小苏打",
                    "item_res": "合格",
                    "item_indicator": "10"
                }
            ]
        }
    ]
    
    # 调用接口
    result = api.submit_inspection_results(
        check_no_join="CN20250713001",
        check_num=1,
        goods=goods_data
    )
    
    print("请求结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    # 运行示例
    example_1_get_pending_samples()
    example_2_submit_inspection_results()