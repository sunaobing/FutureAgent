"""
FUTUREAGENT - 专属智能体点餐交互系统
核心功能：模拟用户智能体、平台智能体、店铺智能体的交互流程，实现个性化点餐推荐
用户偏好：价格适中（10-30元）、少甜、不加糖、少冰
"""
import json
from dataclasses import dataclass
from typing import List, Dict, Optional

# ====================== 数据模型定义 ======================
@dataclass
class UserPreference:
    """用户偏好数据模型"""
    price_range: tuple  # 价格区间 (min, max)
    sugar_level: str    # 糖分偏好（不加糖/少甜/正常/多甜）
    ice_level: str      # 冰度偏好（少冰/去冰/正常/多冰）

@dataclass
class Shop:
    """店铺数据模型"""
    shop_id: str
    shop_name: str
    category: str       # 品类（奶茶/快餐/简餐等）
    avg_price: float    # 均价

@dataclass
class Product:
    """商品数据模型"""
    product_id: str
    product_name: str
    price: float
    sugar_options: List[str]  # 支持的糖分选项
    ice_options: List[str]    # 支持的冰度选项

# ====================== 智能体实现 ======================
class UserAgent:
    """用户专属智能体：管理用户偏好，发起点餐请求"""
    def __init__(self, user_id: str, preference: UserPreference):
        self.user_id = user_id
        self.preference = preference

    def generate_order_request(self) -> Dict:
        """生成标准化的点餐请求（对外仅暴露偏好，不暴露原始数据）"""
        return {
            "user_id": self.user_id,
            "preference": {
                "price_range": self.preference.price_range,
                "sugar_level": self.preference.sugar_level,
                "ice_level": self.preference.ice_level
            },
            "request_type": "food_order"
        }

class PlatformAgent:
    """平台智能体：管理店铺列表，筛选符合用户基础条件的店铺"""
    def __init__(self, platform_name: str, shops: List[Shop]):
        self.platform_name = platform_name
        self.shops = shops

    def filter_shops(self, user_request: Dict) -> List[Shop]:
        """根据用户价格偏好筛选店铺"""
        price_min, price_max = user_request["preference"]["price_range"]
        filtered_shops = []
        for shop in self.shops:
            # 筛选条件：均价在用户价格区间内
            if price_min <= shop.avg_price <= price_max:
                filtered_shops.append(shop)
        return filtered_shops

class ShopAgent:
    """店铺智能体：管理本店商品，筛选符合用户偏好的商品"""
    def __init__(self, shop: Shop, products: List[Product]):
        self.shop = shop
        self.products = products

    def filter_products(self, user_request: Dict) -> List[Product]:
        """根据用户糖分、冰度偏好筛选商品"""
        sugar_pref = user_request["preference"]["sugar_level"]
        ice_pref = user_request["preference"]["ice_level"]
        filtered_products = []
        
        for product in self.products:
            # 筛选条件：商品支持用户的糖分+冰度偏好
            if sugar_pref in product.sugar_options and ice_pref in product.ice_options:
                filtered_products.append(product)
        return filtered_products

# ====================== 交互流程实现 ======================
def run_order_flow(user_agent: UserAgent, platform_agent: PlatformAgent, shop_agents: Dict[str, ShopAgent]):
    """
    执行完整的点餐交互流程：
    1. 用户智能体生成点餐请求
    2. 平台智能体筛选符合条件的店铺
    3. 遍历筛选后的店铺，店铺智能体筛选符合条件的商品
    4. 汇总结果返回给用户
    """
    # Step 1: 用户智能体发起请求
    user_request = user_agent.generate_order_request()
    print(f"📱 用户{user_agent.user_id}发起点餐请求：{json.dumps(user_request, ensure_ascii=False, indent=2)}")

    # Step 2: 平台智能体筛选店铺
    filtered_shops = platform_agent.filter_shops(user_request)
    print(f"\n🏪 平台{platform_agent.platform_name}筛选出符合价格条件的店铺：")
    for shop in filtered_shops:
        print(f"   - {shop.shop_name}（均价：{shop.avg_price}元）")

    # Step 3: 店铺智能体筛选商品
    final_recommendations = []
    for shop in filtered_shops:
        shop_agent = shop_agents.get(shop.shop_id)
        if not shop_agent:
            continue
        
        matched_products = shop_agent.filter_products(user_request)
        if matched_products:
            final_recommendations.append({
                "shop_name": shop.shop_name,
                "products": [{"name": p.product_name, "price": p.price} for p in matched_products]
            })

    # Step 4: 输出最终推荐结果
    print(f"\n🎯 为用户{user_agent.user_id}推荐的最终菜品：")
    if final_recommendations:
        for item in final_recommendations:
            print(f"\n【{item['shop_name']}】")
            for product in item["products"]:
                print(f"   - {product['name']}：{product['price']}元（符合：少甜/不加糖+少冰）")
    else:
        print("   暂无符合所有偏好的商品")

# ====================== 测试运行 ======================
if __name__ == "__main__":
    # 1. 初始化用户偏好（价格适中10-30元、少甜/不加糖、少冰）
    user_pref = UserPreference(
        price_range=(10, 30),
        sugar_level="不加糖",
        ice_level="少冰"
    )
    user_agent = UserAgent(user_id="U001", preference=user_pref)

    # 2. 初始化平台和店铺数据
    test_shops = [
        Shop(shop_id="S001", shop_name="茶颜悦色（步行街店）", category="奶茶", avg_price=18.0),
        Shop(shop_id="S002", shop_name="麦当劳（市中心店）", category="快餐", avg_price=25.0),
        Shop(shop_id="S003", shop_name="星巴克（写字楼店）", category="咖啡", avg_price=35.0)  # 均价超30，会被过滤
    ]
    platform_agent = PlatformAgent(platform_name="美团", shops=test_shops)

    # 3. 初始化店铺商品和店铺智能体
    shop_agents = {
        # 茶颜悦色商品（支持不加糖+少冰）
        "S001": ShopAgent(
            shop=test_shops[0],
            products=[
                Product(
                    product_id="P001",
                    product_name="幽兰拿铁",
                    price=18.0,
                    sugar_options=["不加糖", "少甜", "正常"],
                    ice_options=["少冰", "去冰", "正常"]
                ),
                Product(
                    product_id="P002",
                    product_name="声声乌龙",
                    price=16.0,
                    sugar_options=["不加糖", "少甜"],
                    ice_options=["少冰", "去冰"]
                ),
                Product(
                    product_id="P003",
                    product_name="抹茶葡提",
                    price=19.0,
                    sugar_options=["正常", "多甜"],  # 不支持不加糖，会被过滤
                    ice_options=["少冰", "正常"]
                )
            ]
        ),
        # 麦当劳商品（无冰度/糖分选项，会被过滤）
        "S002": ShopAgent(
            shop=test_shops[1],
            products=[
                Product(
                    product_id="P004",
                    product_name="巨无霸套餐",
                    price=28.0,
                    sugar_options=[],  # 无糖分选项
                    ice_options=[]     # 无冰度选项
                )
            ]
        )
    }

    # 4. 执行点餐流程
    run_order_flow(user_agent, platform_agent, shop_agents)
