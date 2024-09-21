# stats.py

import pymysql
from datetime import datetime
from collections import defaultdict

class ProblemManager:
    def __init__(self, db_config):
        self.db_config = db_config
        self.cache = defaultdict(dict)
        self.conn = self.connect_db()
        self.create_table()

    def connect_db(self):
        """Connect to the MySQL database using PyMySQL."""
        conn = pymysql.connect(**self.db_config)
        return conn

    def create_table(self):
        """Create the problems table if it does not exist."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS problems (
                id INT PRIMARY KEY AUTO_INCREMENT,
                problem_number VARCHAR(255) NOT NULL,
                description TEXT,
                example TEXT,
                solved_date DATE
            )
        """)
        self.conn.commit()
        cursor.close()  # 关闭游标

    def import_data(self, data):
        """Import a list of problem data into the database."""
        cursor = self.conn.cursor()
        
        # 先清空表
        cursor.execute("DELETE FROM problems")
        
        for entry in data:
            problem_number, description, example, solved_date = entry
            cursor.execute("""
                INSERT INTO problems (problem_number, description, example, solved_date)
                VALUES (%s, %s, %s, %s)
            """, (problem_number, description, example, solved_date))
        self.conn.commit()

    def export_data(self):
        """Export all problem data from the database."""
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM problems")
        result = cursor.fetchall()
        cursor.close()  # 关闭游标
        return result

    def count_elements(self):
        """Count the total number of elements in the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM problems")
        total_count = cursor.fetchone()[0]
        cursor.close()  # 关闭游标
        return total_count

    def count_unique_and_duplicates(self):
        """Count the number of unique and duplicate problem numbers."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT problem_number, COUNT(*)
            FROM problems
            GROUP BY problem_number
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        cursor.close()  # 关闭游标
        unique_count = self.count_elements() - len(duplicates)
        return unique_count, len(duplicates)

    def query_problem(self, problem_number):
        """Query problem details by problem number."""
        if problem_number in self.cache:
            return self.cache[problem_number]

        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM problems WHERE problem_number = %s", (problem_number,))
        result = cursor.fetchone()
        cursor.close()  # 关闭游标

        if result:
            self.cache[problem_number] = result
        return result

    def cache_data(self, problem_number):
        """Cache problem data for quick access."""
        problem_data = self.query_problem(problem_number)
        if problem_data:
            self.cache[problem_number] = problem_data

    def query_cache(self, problem_number):
        """Query data directly from the cache."""
        return self.cache.get(problem_number, "Problem not found in cache")

    def calculate_difference(self, solved_set, completed_set):
        """Calculate the difference between solved and completed sets."""
        difference_solved_completed = solved_set - completed_set
        difference_completed_solved = completed_set - solved_set
        return difference_solved_completed, difference_completed_solved

    def close_connection(self):
        """Close the database connection."""
        if self.conn.open:  # pymysql用 open 代替 is_connected
            self.conn.close()

# 示例数据
solved = [
    "2", "面01.02", "58", "9", "1108", "LCR 182", "1486", "771", "1431", "832",
    "LCP 06", "1450", "1757", "1313", "2114", "1480", "1725", "14", "LCP 01", "2006",
    "561", "1252", "1920", "LCR 140", "1570", "2315", "2413", "1678", "1769", "1684",
    "2535", "2185", "1378", "94", "145", "144", "1683", "26", "613", "175", "1470",
    "2619", "35", "3", "1729", "1050", "2667", "1119", "1142", "1741", "1693", "面17.04",
    "1365", "1873", "面16.07", "1251", "1789", "620", "1890", "1581", "627", "182",
    "1795", "744", "610", "2678", "2656", "2441", "704", "1455", "1672", "1550", "2283",
    "2418", "2574", "2490", "1623", "1114", "2651", "2652", "1979", "1518", "2351", "1512",
    "1773", "2703", "1929", "1342", "728", "2810", "LCR 003", "2236", "509", "1281", "1748",
    "303", "1389", "2319", "2544", "228", "2824", "229", "872", "1812", "461", "2295", "2769",
    "2828", "136", "191", "231", "1688", "349", "2103", "342", "2520", "326", "1832", "1134",
    "2331", "541", "2586", "LCP 50", "2974", "2894", "3194", "2037", "804", "2886", "2648",
    "3065", "2723", "1476", "LCR 158", "LCR 189", "3099", "2951", "2923", "3162", "3146",
    "3151", "2878", "3168", "2864", "1351", "3190", "2888", "2798", "2670", "2965", "3033",
    "42", "2620", "3232", "27", "1732", "2882", "2194", "2220", "28", "2377", "2885", "1913",
    "153"
]

completed = [
    "1539", "1", "2", "面01.02", "58", "9", "1051", "2235", "LCR 182", "1486", "1431",
    "2011", "832", "LCP 06", "1450", "1313", "2114", "1480", "1725", "14", "2006", "LCP 01",
    "561", "804", "2037", "1252", "2367", "1920", "2469", "2315", "LCR 140", "1570", "2413",
    "1678", "13", "1769", "1684", "2535", "2500", "760", "1068", "LCP 17", "94", "1729", "144",
    "1821", "613", "175", "1683", "1470", "26", "35", "1108", "3", "1378", "2619", "1050", "2667",
    "1741", "2325", "1142", "1119", "145", "2185", "1266", "1784", "1890", "LCP 66", "771",
    "面17.04", "1365", "1623", "1873", "2356", "面16.07", "1789", "1251", "1693", "1757", "610",
    "914", "620", "1581", "627", "182", "1795", "744", "2656", "2678", "2441", "2373", "1455",
    "2574", "1672", "1550", "2490", "2283", "2418", "LCR 135", "2432", "1114", "2651", "2652",
    "1979", "506", "1518", "2351", "面16.01", "2341", "860", "1773", "1929", "1512", "2357",
    "1827", "LCR 189", "2703", "922", "728", "1342", "258", "2621", "2176", "1603", "LCR 042",
    "171", "1720", "344", "338", "2810", "LCR 003", "1572", "509", "2236", "1281", "1389", "1748",
    "303", "704", "2319", "2544", "1528", "228", "2824", "229", "872", "1030", "1812", "461",
    "2295", "191", "2769", "136", "2828", "1688", "349", "2103", "231", "326", "2520", "342",
    "LCR 158", "1832", "1828", "1134", "LCP 44", "2331", "2496", "2586", "557", "2485", "2506",
    "541", "1837", "LCP 50", "2427", "1228", "2148", "1791", "2974", "2894", "3194", "2942",
    "3174", "3110", "2960", "2697", "2859", "3079", "面02.02", "1227", "2881", "118", "2744",
    "2879", "2884", "2798", "2670", "2965", "2888", "2710", "2796", "2864", "1351", "3190",
    "3168", "3151", "2878", "42", "2723", "3146", "2923", "2951", "3099", "3162", "2886", "2648",
    "3065", "3033", "2620", "3232", "27", "1732", "2220", "1476", "2194", "2882", "28", "51",
    "70", "78", "146", "160", "207", "994", "1662", "1913", "2377", "2885"
]

# 将 solved 和 completed 数据打包成带有描述、示例和日期的元组列表
solved_data = [(problem, "Solved description", "Solved example", datetime.now().date()) for problem in solved]
completed_data = [(problem, "Completed description", "Completed example", datetime.now().date()) for problem in completed]

# 创建 ProblemManager 实例
db_config = {
    'user': 'root',
    'password': 'Zqy19991214!',
    'host': 'localhost',
    'database': 'mysql',
    'charset': 'utf8mb4'
}

manager = ProblemManager(db_config)

# 导入数据
manager.import_data(solved_data)
manager.import_data(completed_data)

# 计算元素总数
total_count = manager.count_elements()
print("Total Elements:", total_count)

# 计算唯一值和重复值
unique_count, duplicates_count = manager.count_unique_and_duplicates()
print(f"Unique: {unique_count}, Duplicates: {duplicates_count}")

# 计算差集
solved_set = set(solved)
completed_set = set(completed)
diff_solved_completed, diff_completed_solved = manager.calculate_difference(solved_set, completed_set)
print(f"Difference (Solved - Completed): {diff_solved_completed}")
print(f"Difference (Completed - Solved): {diff_completed_solved}")

# 导出数据
exported_data = manager.export_data()
# print("Exported Data:", exported_data)

# 查询特定问题
problem = manager.query_problem("2")
print("Queried Problem:", problem)

# 缓存和查询缓存
manager.cache_data("2")
cached_problem = manager.query_cache("2")
print("Cached Problem:", cached_problem)

# 关闭连接
manager.close_connection()
