class FootballPredictionSystem:
    def __init__(self):
        self.matches = {}
        self.leagues = {
            "1": "英超 (Premier League)",
            "2": "西甲 (La Liga)", 
            "3": "德甲 (Bundesliga)",
            "4": "意甲 (Serie A)",
            "5": "法甲 (Ligue 1)",
            "6": "英冠 (Championship)",
            "7": "德乙 (2. Bundesliga)",
            "8": "法乙 (Ligue 2)", 
            "9": "日职联 (J1 League)",
            "10": "日职乙 (J2 League)",
            "11": "韩K联 (K League 1)",
            "12": "巴甲 (Brasileirão)"
        }
    
    def add_match(self, match_id, league_code, am_odds, wl_odds, hg_odds, lb_odds=None):
        """
        添加比赛数据
        match_id: 比赛编号
        league_code: 联赛代码
        am_odds: 澳门初盘赔率 [胜, 平, 负]
        wl_odds: 威廉希尔初盘赔率 [胜, 平, 负]
        hg_odds: 皇冠初盘赔率 [胜, 平, 负]
        lb_odds: 立博初盘赔率 [胜, 平, 负] (可选)
        """
        if league_code not in self.leagues:
            return "无效的联赛代码"
        
        self.matches[match_id] = {
            'league': league_code,
            'league_name': self.leagues[league_code],
            'am': am_odds,
            'wl': wl_odds,
            'hg': hg_odds,
            'lb': lb_odds
        }
        return f"比赛 {match_id} ({self.leagues[league_code]}) 数据已添加"
    
    def get_lowest_odds(self, odds):
        """获取最低赔率"""
        return min(odds)
    
    def get_odds_combination_str(self, odds):
        """获取赔率组合字符串，格式：胜+平+负"""
        return f"{odds[0]}+{odds[1]}+{odds[2]}"
    
    def analyze_match(self, match_id):
        """分析比赛并给出判断结果"""
        if match_id not in self.matches:
            return "比赛数据不存在"
        
        match_data = self.matches[match_id]
        league_code = match_data['league']
        am_odds = match_data['am']
        wl_odds = match_data['wl']
        hg_odds = match_data['hg']
        
        # 计算各公司最低赔率
        am_min = self.get_lowest_odds(am_odds)
        wl_min = self.get_lowest_odds(wl_odds)
        hg_min = self.get_lowest_odds(hg_odds)
        
        # 计算平局赔率
        am_draw = am_odds[1]
        wl_draw = wl_odds[1]
        hg_draw = hg_odds[1]
        
        results = []
        
        # 根据联赛选择分析规则
        if league_code == "7":  # 德乙专用规则
            results.extend(self.analyze_bundesliga2_rules(wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min))
        else:
            # 其他联赛使用通用规则（包括日职联专用规则）
            results.extend(self.analyze_general_rules(wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min, league_code))
        
        return self.format_result(match_id, match_data, results)
    
    def analyze_bundesliga2_rules(self, wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min):
        """德乙专用规则分析"""
        results = []
        
        # 规则1: 上盘规则
        if self.check_upper_rules(wl_odds, hg_min, wl_min, hg_draw, wl_draw):
            results.append("德乙上盘规则触发 -> 上盘/低赔率方")
        
        # 规则2: 下盘规则  
        if self.check_lower_rules(wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min):
            results.append("德乙下盘规则触发 -> 下盘/高赔率方")
        
        # 规则3: 低水规则
        if self.check_low_water_rules(am_min):
            results.append("德乙低水规则触发 -> 低水方(低赔率方)")
        
        # 规则4: 高水不败规则
        if self.check_high_water_rules(am_min, wl_min):
            results.append("德乙高水不败规则触发 -> 高水不败(高赔率方不败)")
        
        # 规则5: 威廉希尔特定组合
        if self.check_wl_specific_combinations(wl_odds, wl_draw):
            results.append("德乙威廉希尔特定组合触发 -> 相应方向")
        
        return results
    
    def analyze_general_rules(self, wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min, league_code):
        """通用规则分析 (适用于其他联赛)"""
        results = []
        league_name = self.leagues[league_code]
        
        # 日职联专用规则
        if league_code == "9":  # 日职联
            results.extend(self.analyze_j1_league_rules(wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min))
            return results
        
        # 日职乙专用规则
        if league_code == "10":  # 日职乙
            results.extend(self.analyze_j2_league_rules(wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min))
            return results
        
        # 英冠专用规则
        if league_code == "6":  # 英冠
            results.extend(self.analyze_championship_rules(wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min))
            return results
        
        # 法乙专用规则
        if league_code == "8":  # 法乙
            results.extend(self.analyze_ligue2_rules(wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min))
            return results
        
        # 基础赔率分析
        if am_min < 1.80:
            results.append(f"{league_name} 强队主导 -> 建议支持低赔率方")
        elif am_min > 2.50:
            results.append(f"{league_name} 弱队有机会 -> 建议关注高赔率方")
        
        # 赔率差异分析
        am_wl_diff = abs(am_min - wl_min)
        if am_wl_diff > 0.10:
            results.append(f"{league_name} 赔率差异较大 -> 存在分歧，谨慎判断")
        
        # 平局赔率分析
        if wl_draw < 3.00:
            results.append(f"{league_name} 平局概率较高 -> 考虑平局选项")
        elif wl_draw > 3.80:
            results.append(f"{league_name} 分胜负概率高 -> 避开平局")
        
        # 五大联赛特殊规则
        if league_code in ["1", "2", "3", "4", "5"]:
            if 1.30 <= am_min <= 1.60:
                results.append(f"{league_name} 超级强队 -> 强烈建议支持低赔率方")
        
        # 亚洲联赛特殊规则  
        if league_code in ["9", "10", "11"]:
            if 1.70 <= am_min <= 2.20:
                results.append(f"{league_name} 均势对决 -> 建议分析主客场因素")
        
        # 巴甲特殊规则
        if league_code == "12":
            if wl_draw > 3.50:
                results.append(f"{league_name} 巴甲攻击性强 -> 大比分概率高")
        
        return results
    
    def analyze_j1_league_rules(self, wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min):
        """日职联专用规则分析"""
        results = []
        
        # 上盘规则（支持低赔率方）
        if self.check_j1_upper_rules(wl_odds, hg_min, wl_min, hg_draw, wl_draw):
            results.append("日职联上盘规则触发 -> 上盘/低赔率方")
        
        # 下盘规则（支持高赔率方）
        if self.check_j1_lower_rules(wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min):
            results.append("日职联下盘规则触发 -> 下盘/高赔率方")
        
        # 低水方规则
        if self.check_j1_low_water_rules(am_min, wl_min):
            results.append("日职联低水方规则触发 -> 低水方(低赔率方)")
        
        return results
    
    def check_j1_upper_rules(self, wl_odds, hg_min, wl_min, hg_draw, wl_draw):
        """检查日职联上盘规则"""
        hg_wl_diff = hg_min - wl_min
        
        # HG-WL差值规则组
        # HG-WL ≥ 0.2
        if hg_wl_diff >= 0.2:
            return True
        
        # 0.2 > HG-WL ≥ 0.1，且 WLD ≤ HGD
        if 0.1 <= hg_wl_diff < 0.2 and wl_draw <= hg_draw:
            return True
        
        # HG-WL = 0.09, 0.02, -0.05, -0.06
        j1_specific_diffs = [0.09, 0.02, -0.05, -0.06]
        for diff in j1_specific_diffs:
            if abs(hg_wl_diff - diff) < 0.01:
                return True
        
        # 威廉希尔特定赔率: WL = 1.40, 1.44, 1.57, 1.88
        j1_wl_specific = [1.40, 1.44, 1.57, 1.88]
        for odds in j1_wl_specific:
            if abs(wl_min - odds) < 0.02:
                return True
        
        return False
    
    def check_j1_lower_rules(self, wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min):
        """检查日职联下盘规则"""
        wl_hg_diff = wl_min - hg_min
        hg_wl_diff = hg_min - wl_min
        
        # WL-HG差值规则组
        # WL-HG ≥ 0.10，且 WLD < HGD
        if wl_hg_diff >= 0.10 and wl_draw < hg_draw:
            return True
        
        # HG-WL = 0.07, 0.05, 0.04, 0.03, 0.01, -0.02, -0.03, -0.08
        j1_hg_wl_diffs = [0.07, 0.05, 0.04, 0.03, 0.01, -0.02, -0.03, -0.08]
        for diff in j1_hg_wl_diffs:
            if abs(hg_wl_diff - diff) < 0.01:
                return True
        
        # 威廉希尔特定赔率: WL = 2.62
        if abs(wl_min - 2.62) < 0.02:
            return True
        
        # 高水方规则组
        # 2.10 < AM < 2.19，AM > 2.40，AM > WL
        if (2.10 < am_min < 2.19) or (am_min > 2.40 and am_min > wl_min):
            return True
        
        # AM > 2.00，AM-WL = 0.02
        am_wl_diff = am_min - wl_min
        if am_min > 2.00 and abs(am_wl_diff - 0.02) < 0.01:
            return True
        
        return False
    
    def check_j1_low_water_rules(self, am_min, wl_min):
        """检查日职联低水方规则"""
        am_wl_diff = am_min - wl_min
        
        # AM > 2.00，AM-WL = 0.03
        if am_min > 2.00 and abs(am_wl_diff - 0.03) < 0.01:
            return True
        
        return False
    
    def analyze_j2_league_rules(self, wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min):
        """日职乙专用规则分析"""
        results = []
        
        # 上盘规则（支持低赔率方）
        if self.check_j2_upper_rules(wl_odds, hg_min, wl_min, hg_draw, wl_draw):
            results.append("日职乙上盘规则触发 -> 上盘/低赔率方")
        
        # 下盘规则（支持高赔率方）
        if self.check_j2_lower_rules(wl_odds, hg_min, wl_min, hg_draw, wl_draw):
            results.append("日职乙下盘规则触发 -> 下盘/高赔率方")
        
        # 高指方规则（支持高赔率方）
        if self.check_j2_high_pointer_rules(am_min, wl_min):
            results.append("日职乙高指方规则触发 -> 高指方(高赔率方)")
        
        return results
    
    def check_j2_upper_rules(self, wl_odds, hg_min, wl_min, hg_draw, wl_draw):
        """检查日职乙上盘规则"""
        hg_wl_diff = hg_min - wl_min
        
        # HG-WL差值规则
        # HG-WL = 0.01 (当WL D >= HGD), 0.05
        if abs(hg_wl_diff - 0.01) < 0.005 and wl_draw >= hg_draw:
            return True
        if abs(hg_wl_diff - 0.05) < 0.005:
            return True
        
        # 威廉希尔特定赔率: WL = 1.44, 1.57, 1.60, 1.61, 1.65, 1.73
        j2_wl_specific = [1.44, 1.57, 1.60, 1.61, 1.65, 1.73]
        for odds in j2_wl_specific:
            if abs(wl_min - odds) < 0.02:
                return True
        
        return False
    
    def check_j2_lower_rules(self, wl_odds, hg_min, wl_min, hg_draw, wl_draw):
        """检查日职乙下盘规则"""
        hg_wl_diff = hg_min - wl_min
        wl_hg_diff = wl_min - hg_min
        
        # HG-WL差值规则组
        # 0.1 < HG-WL < 0.2
        if 0.1 < hg_wl_diff < 0.2:
            return True
        
        # 平路 WL-HG >= 0.3
        if wl_hg_diff >= 0.3:
            return True
        
        # HG-WL = 0.08, 0.04, 0.03, 0.02, -0.01, -0.03, -0.09
        j2_hg_wl_diffs = [0.08, 0.04, 0.03, 0.02, -0.01, -0.03, -0.09]
        for diff in j2_hg_wl_diffs:
            if abs(hg_wl_diff - diff) < 0.005:
                return True
        
        # 威廉希尔特定赔率: WL = 1.95, 2.35, 2.55
        j2_wl_single = [1.95, 2.35, 2.55]
        for odds in j2_wl_single:
            if abs(wl_min - odds) < 0.02:
                return True
        
        # 威廉希尔特定组合: 2.15+3.20, 2.20+3.10, 2.45+3.00, 2.60+3.10
        j2_wl_combinations = [
            [2.15, 3.20], [2.20, 3.10], [2.45, 3.00], [2.60, 3.10]
        ]
        
        for combo in j2_wl_combinations:
            # 检查最低赔率是否匹配第一个值，平局赔率是否匹配第二个值
            if abs(wl_min - combo[0]) < 0.02 and abs(wl_odds[1] - combo[1]) < 0.05:
                return True
        
        return False
    
    def check_j2_high_pointer_rules(self, am_min, wl_min):
        """检查日职乙高指方规则"""
        am_wl_diff = am_min - wl_min
        
        # 澳门赔率区间: 2.10 < AM < 2.19 (且 AM > WL)
        if 2.10 < am_min < 2.19 and am_min > wl_min:
            return True
        
        # AM-WL差值规则: AM > 2.00, AM-WL = 0.01~0.03; 0.07~0.08
        if am_min > 2.00:
            if 0.01 <= am_wl_diff <= 0.03:
                return True
            if 0.07 <= am_wl_diff <= 0.08:
                return True
        
        return False
    
    def analyze_ligue2_rules(self, wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min):
        """法乙专用规则分析"""
        results = []
        
        # 上盘规则（支持低赔率方）
        if self.check_ligue2_upper_rules(wl_odds, am_min):
            results.append("法乙上盘规则触发 -> 上盘/低赔率方")
        
        # 下盘规则（支持高赔率方）
        if self.check_ligue2_lower_rules(wl_odds, am_min, wl_min):
            results.append("法乙下盘规则触发 -> 下盘/高赔率方")
        
        return results
    
    def check_ligue2_upper_rules(self, wl_odds, am_min):
        """检查法乙上盘规则"""
        wl_min = min(wl_odds)
        
        # 威廉希尔单一赔率: WL = 1.44, 1.60
        ligue2_wl_single = [1.44, 1.60]
        for odds in ligue2_wl_single:
            if abs(wl_min - odds) < 0.02:
                return True
        
        # 威廉希尔赔率组合: WL = 2.05+3.00, 2.45+3.20, 2.50+2.90
        ligue2_wl_combinations = [
            [2.05, 3.00], [2.45, 3.20], [2.50, 2.90]
        ]
        
        for combo in ligue2_wl_combinations:
            # 检查最低赔率是否匹配第一个值，平局赔率是否匹配第二个值
            if abs(wl_min - combo[0]) < 0.03 and abs(wl_odds[1] - combo[1]) < 0.05:
                return True
        
        # 澳门低赔率: AM < 1.70
        if am_min < 1.70:
            return True
        
        return False
    
    def check_ligue2_lower_rules(self, wl_odds, am_min, wl_min):
        """检查法乙下盘规则"""
        am_wl_diff = am_min - wl_min
        
        # 威廉希尔单一赔率: WL = 2.60, 2.62, 2.40, 2.70
        ligue2_wl_single = [2.60, 2.62, 2.40, 2.70]
        for odds in ligue2_wl_single:
            if abs(wl_min - odds) < 0.02:
                return True
        
        # 威廉希尔赔率组合: WL = 2.30+3.10, 2.45+2.90
        ligue2_wl_combinations = [
            [2.30, 3.10], [2.45, 2.90]
        ]
        
        for combo in ligue2_wl_combinations:
            # 检查最低赔率是否匹配第一个值，平局赔率是否匹配第二个值
            if abs(wl_min - combo[0]) < 0.03 and abs(wl_odds[1] - combo[1]) < 0.05:
                return True
        
        # 澳门赔率区间: 2.20 < AM < 2.49
        if 2.20 < am_min < 2.49:
            return True
        
        # AM-WL差值规则: AM > 2.00, AM-WL = 0.05
        if am_min > 2.00 and abs(am_wl_diff - 0.05) < 0.01:
            return True
        
        # AM-WL差值规则: AM > 2.00, AM-WL = 0.1~0.19
        if am_min > 2.00 and 0.1 <= am_wl_diff <= 0.19:
            return True
        
        return False
    
    def analyze_championship_rules(self, wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min):
        """英冠专用规则分析"""
        results = []
        
        # 上盘规则（支持低赔率方）
        if self.check_championship_upper_rules(wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min):
            results.append("英冠上盘规则触发 -> 上盘/低赔率方")
        
        # 下盘规则（支持高赔率方）
        if self.check_championship_lower_rules(wl_odds, hg_min, wl_min, am_min):
            results.append("英冠下盘规则触发 -> 下盘/高赔率方")
        
        return results
    
    def check_championship_upper_rules(self, wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min):
        """检查英冠上盘规则"""
        hg_wl_diff = hg_min - wl_min
        hgd_wld_diff = hg_draw - wl_draw
        
        # 澳门低赔率: AM < 1.70
        if am_min < 1.70:
            return True
        
        # 威廉希尔特定赔率: WL = 1.50, 1.44, 1.73, 1.88
        championship_wl_specific = [1.50, 1.44, 1.73, 1.88]
        for odds in championship_wl_specific:
            if abs(wl_min - odds) < 0.02:
                return True
        
        # 威廉希尔特定赔率: WL = 1.33, 1.57, 1.70, 1.78, 1.95
        championship_wl_additional = [1.33, 1.57, 1.70, 1.78, 1.95]
        for odds in championship_wl_additional:
            if abs(wl_min - odds) < 0.02:
                return True
        
        # HG-WL差值规则: HG-WL ≥ 0.20
        if hg_wl_diff >= 0.20:
            return True
        
        # HGD-WLD差值规则: HGD-WLD = 0.45, 0.20
        if abs(hgd_wld_diff - 0.45) < 0.05 or abs(hgd_wld_diff - 0.20) < 0.05:
            return True
        
        # 其他HG-WL规则: HG-WL = 0.04, 0.02, -0.02, -0.08
        championship_hg_wl_diffs = [0.04, 0.02, -0.02, -0.08]
        for diff in championship_hg_wl_diffs:
            if abs(hg_wl_diff - diff) < 0.01:
                return True
        
        # HG-WL < 0.5
        if hg_wl_diff < 0.5:
            return True
        
        return False
    
    def check_championship_lower_rules(self, wl_odds, hg_min, wl_min, am_min):
        """检查英冠下盘规则"""
        hg_wl_diff = hg_min - wl_min
        am_wl_diff = am_min - wl_min
        
        # 澳门高赔率: AM > 2.40
        if am_min > 2.40:
            return True
        
        # AM-WL差值规则: AM > 2.00, AM-WL = 0.1
        if am_min > 2.00 and abs(am_wl_diff - 0.1) < 0.01:
            return True
        
        # AM-WL差值规则: AM > 2.00, AM-WL = 0.01~0.02
        if am_min > 2.00 and 0.01 <= am_wl_diff <= 0.02:
            return True
        
        # 威廉希尔特定赔率: WL = 2.60, 2.40
        championship_wl_lower = [2.60, 2.40]
        for odds in championship_wl_lower:
            if abs(wl_min - odds) < 0.02:
                return True
        
        # HG-WL差值规则: HG-WL = 0.09, 0.08, 0.07, 0.06, 0.01
        championship_hg_wl_diffs = [0.09, 0.08, 0.07, 0.06, 0.01]
        for diff in championship_hg_wl_diffs:
            if abs(hg_wl_diff - diff) < 0.005:
                return True
        
        # HG-WL > 0.5
        if hg_wl_diff > 0.5:
            return True
        
        return False
    
    def check_upper_rules(self, wl_odds, hg_min, wl_min, hg_draw, wl_draw):
        """检查上盘规则"""
        # 规则: WL=1.70, 2.37+3.30 (近似匹配)
        if abs(wl_min - 1.70) < 0.05:
            if wl_odds[1] > 2.30 and wl_odds[2] > 3.20:
                return True
        
        # 规则: HG-WL=0.08
        if abs((hg_min - wl_min) - 0.08) < 0.01:
            return True
        
        # 规则: WL=2.00 + D +3.40/3.60
        if abs(wl_min - 2.00) < 0.05:
            if wl_odds[1] > 3.30 and (wl_odds[2] > 3.35 or wl_odds[2] > 3.55):
                return True
        
        # 规则: WL=2.10+3.30
        if abs(wl_min - 2.10) < 0.05 and abs(wl_odds[1] - 3.30) < 0.05:
            return True
        
        return False
    
    def check_lower_rules(self, wl_odds, hg_min, wl_min, hg_draw, wl_draw, am_min):
        """检查下盘规则"""
        # 威廉希尔特定组合规则
        wl_combinations = [
            [2.60, 2.50, 3.10], [2.25, 3.20, 0], [2.15, 3.10, 0],
            [2.00, 3.40, 0], [2.15, 3.30, 0], [2.45, 3.20, 0],
            [2.45, 3.25, 0], [2.50, 3.00, 0]
        ]
        
        for combo in wl_combinations:
            if (abs(wl_odds[0] - combo[0]) < 0.05 or abs(wl_odds[1] - combo[0]) < 0.05 or abs(wl_odds[2] - combo[0]) < 0.05):
                if combo[1] > 0 and (abs(wl_odds[1] - combo[1]) < 0.05 or abs(wl_odds[2] - combo[1]) < 0.05):
                    return True
        
        # HG-WL差值规则
        hg_wl_diff = hg_min - wl_min
        if 0.10 < hg_wl_diff <= 0.20:
            return True
        if abs(hg_wl_diff - 0.10) < 0.01:
            return True
        if abs(hg_wl_diff + 0.06) < 0.01 or abs(hg_wl_diff + 0.09) < 0.01:
            return True
        if abs(hg_wl_diff - 0.04) < 0.01 or abs(hg_wl_diff - 0.03) < 0.01 or abs(hg_wl_diff - 0.01) < 0.01:
            return True
        
        # WL-HG=0.10
        if abs((wl_min - hg_min) - 0.10) < 0.01:
            return True
        
        # HGD-WLD规则
        if abs((hg_draw - wl_draw) - 0.30) < 0.05:
            return True
        if abs((hg_draw - wl_draw) - 0.25) < 0.05:
            return True
        
        # 容让规则 (简化处理)
        if 1.50 <= wl_min < 2.00:
            return True
        
        return False
    
    def check_low_water_rules(self, am_min):
        """检查低水规则"""
        # 1.70<AM<1.89
        return 1.70 < am_min < 1.89
    
    def check_high_water_rules(self, am_min, wl_min):
        """检查高水不败规则"""
        am_wl_diff = am_min - wl_min
        
        # AM>2.00, AM-WL=0.05
        if am_min > 2.00 and abs(am_wl_diff - 0.05) < 0.01:
            return True
        
        # AM<2.00, AM-WL=0.02~0.03  
        if am_min < 2.00 and 0.02 <= am_wl_diff <= 0.03:
            return True
        
        return False
    
    def check_wl_specific_combinations(self, wl_odds, wl_draw):
        """检查威廉希尔特定组合"""
        wl_min = min(wl_odds)
        
        # WL=1.80+3.70+4.20
        if abs(wl_min - 1.80) < 0.05:
            if wl_odds[1] > 3.65 and wl_odds[2] > 4.15:
                return True
        
        # WL=1.91, +(D>=3.50)
        if abs(wl_min - 1.91) < 0.05 and wl_draw >= 3.50:
            return True
        
        # D=3.25相关组合
        if abs(wl_draw - 3.25) < 0.05:
            return True
        
        return False
    
    def format_result(self, match_id, match_data, results):
        """格式化输出结果"""
        output = [f"\n=== 比赛 {match_id} 分析结果 ==="]
        output.append(f"联赛: {match_data['league_name']}")
        output.append(f"澳门初盘: {match_data['am'][0]:.2f} | {match_data['am'][1]:.2f} | {match_data['am'][2]:.2f}")
        output.append(f"威廉希尔: {match_data['wl'][0]:.2f} | {match_data['wl'][1]:.2f} | {match_data['wl'][2]:.2f}")  
        output.append(f"皇冠初盘: {match_data['hg'][0]:.2f} | {match_data['hg'][1]:.2f} | {match_data['hg'][2]:.2f}")
        output.append("")
        
        if results:
            output.append("触发规则:")
            for i, result in enumerate(results, 1):
                output.append(f"{i}. {result}")
            
            # 综合判断
            upper_count = sum(1 for r in results if "上盘" in r or "低赔率方" in r or "低水方" in r or "强队" in r or "超级强队" in r)
            lower_count = sum(1 for r in results if "下盘" in r or "高赔率方" in r or "弱队" in r)
            draw_count = sum(1 for r in results if "平局" in r)
            
            output.append("")
            output.append("=== 综合判断 ===")
            if upper_count > lower_count and upper_count > draw_count:
                output.append("🔥 建议: 支持上盘/低赔率方")
            elif lower_count > upper_count and lower_count > draw_count:
                output.append("🔥 建议: 支持下盘/高赔率方") 
            elif draw_count > 0 and draw_count >= upper_count and draw_count >= lower_count:
                output.append("🟡 建议: 关注平局选项")
            else:
                output.append("⚖️  信号混合，建议谨慎")
        else:
            output.append("❌ 未触发任何已知规则")
        
        return "\n".join(output)

    def show_leagues(self):
        """显示所有支持的联赛"""
        print("\n=== 支持的联赛列表 ===")
        print("五大联赛:")
        for code in ["1", "2", "3", "4", "5"]:
            print(f"  {code}. {self.leagues[code]}")
        
        print("\n二级联赛:")
        for code in ["6", "7", "8"]:
            print(f"  {code}. {self.leagues[code]}")
        
        print("\n亚洲联赛:")
        for code in ["9", "10", "11"]:
            print(f"  {code}. {self.leagues[code]}")
        
        print("\n南美联赛:")
        for code in ["12"]:
            print(f"  {code}. {self.leagues[code]}")
        print()

# 创建系统实例
system = FootballPredictionSystem()

# 交互界面
def interactive_system():
    print("=== 足球赛果判断系统 (多联赛版) ===")
    print("输入格式说明:")
    print("- 比赛编号: 任意字符串")
    print("- 联赛代码: 见联赛列表")
    print("- 赔率格式: 胜 平 负 (空格分隔)")
    print("- 输入 'leagues' 查看联赛列表")
    print("- 输入 'quit' 退出系统")
    print("- 输入 'analyze [比赛编号]' 分析比赛")
    print()
    
    while True:
        try:
            command = input("请输入指令: ").strip()
            
            if command.lower() == 'quit':
                print("系统退出")
                break
            
            if command.lower() == 'leagues':
                system.show_leagues()
                continue
                
            if command.startswith('analyze '):
                match_id = command[8:].strip()
                result = system.analyze_match(match_id)
                print(result)
                continue
            
            # 添加比赛数据
            match_id = input("请输入比赛编号: ").strip()
            
            # 显示联赛选择
            system.show_leagues()
            league_code = input("请选择联赛代码: ").strip()
            
            if league_code not in system.leagues:
                print("无效的联赛代码，请重新选择")
                continue
            
            print("请输入澳门初盘赔率(胜 平 负): ", end="")
            am_input = input().strip().split()
            am_odds = [float(x) for x in am_input]
            
            print("请输入威廉希尔初盘赔率(胜 平 负): ", end="")
            wl_input = input().strip().split() 
            wl_odds = [float(x) for x in wl_input]
            
            print("请输入皇冠初盘赔率(胜 平 负): ", end="")
            hg_input = input().strip().split()
            hg_odds = [float(x) for x in hg_input]
            
            # 添加数据
            result = system.add_match(match_id, league_code, am_odds, wl_odds, hg_odds)
            print(result)
            
            # 自动分析
            analysis = system.analyze_match(match_id)
            print(analysis)
            print("\n" + "="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n系统退出")
            break
        except Exception as e:
            print(f"输入错误: {e}")
            print("请检查输入格式")

# 启动交互系统
if __name__ == "__main__":
    interactive_system()