import heapq
import time
from collections import deque


class PerformanceMetrics:
    def __init__(self, algorithm_name: str):
        self.algorithm_name = algorithm_name
        self.nodes_explored = 0
        self.start_time = None
        self.end_time = None
        self.path_found = False
        self.path_length = 0

    def start_timing(self):
        self.start_time = time.time()
        self.nodes_explored = 0

    def end_timing(self, path=None):
        self.end_time = time.time()
        if path:
            self.path_found = True
            self.path_length = len(path)

    def record_node_exploration(self):
        self.nodes_explored += 1

    @property
    def execution_time(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0

    def to_dict(self):
        return {
            'algorithm': self.algorithm_name,
            'execution_time_ms': round(self.execution_time * 1000, 3),
            'nodes_explored': self.nodes_explored,
            'path_found': self.path_found,
            'path_length': self.path_length,
            'efficiency_score': (self.execution_time * 1000) + (self.nodes_explored * 0.1)
        }


class PathfindingComparator:
    EMOTION_HIERARCHY = {
        'happy': 1, 'neutral': 2, 'confused': 3,
        'tired': 4, 'sad': 5, 'anxious': 5, 'angry': 6
    }

    def __init__(self, memory_map):
        self.memory_map = memory_map

    def get_neighbors(self, emotion: str):
        neighbors = []
        for next_emotion in self.memory_map.get("graph_connections", {}).get(emotion, []):
            key = (emotion, next_emotion)
            if key in self.memory_map.get("transitions", {}):
                actions = self.memory_map["transitions"][key]
                if actions:
                    avg_success = sum(a.get('success_count', 1) for a in actions) / len(actions)
                    neighbors.append((next_emotion, 1.0 / max(0.1, avg_success)))

        if not neighbors:
            for name in self.EMOTION_HIERARCHY:
                if name != emotion:
                    cost = abs(self.EMOTION_HIERARCHY[emotion] - self.EMOTION_HIERARCHY[name])
                    neighbors.append((name, cost))
        return neighbors

    def get_reverse_neighbors(self, emotion: str):
        neighbors = []
        for (from_e, to_e), actions in self.memory_map.get("transitions", {}).items():
            if to_e == emotion and actions:
                avg_success = sum(a.get('success_count', 1) for a in actions) / len(actions)
                neighbors.append((from_e, 1.0 / max(0.1, avg_success)))

        if not neighbors:
            for name in self.EMOTION_HIERARCHY:
                if name != emotion:
                    cost = abs(self.EMOTION_HIERARCHY[emotion] - self.EMOTION_HIERARCHY[name])
                    neighbors.append((name, cost))
        return neighbors

    def heuristic(self, current: str, target: str) -> float:
        return abs(self.EMOTION_HIERARCHY.get(current, 3) - self.EMOTION_HIERARCHY.get(target, 3))

    def astar_search(self, start: str, goal: str, max_depth: int = 8):
        metrics = PerformanceMetrics("A*")
        metrics.start_timing()

        open_set = [(self.heuristic(start, goal), 0, start, [start])]
        closed_set = set()
        g_scores = {start: 0}

        while open_set:
            f_score, g_score, current, path = heapq.heappop(open_set)
            if current in closed_set:
                continue
            metrics.record_node_exploration()
            closed_set.add(current)

            if current == goal:
                metrics.end_timing(path)
                return path, metrics
            if len(path) >= max_depth:
                continue

            for neighbor, cost in self.get_neighbors(current):
                if neighbor in closed_set:
                    continue
                tentative_g = g_score + cost
                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g
                    heapq.heappush(open_set, (
                        tentative_g + self.heuristic(neighbor, goal),
                        tentative_g, neighbor, path + [neighbor]
                    ))

        metrics.end_timing()
        return [], metrics

    def bidirectional_search(self, start: str, goal: str, max_depth: int = 8):
        metrics = PerformanceMetrics("Bidirectional")
        metrics.start_timing()

        if start == goal:
            metrics.end_timing([start])
            return [start], metrics

        fwd_queue = deque([(start, [start], 0)])
        bwd_queue = deque([(goal, [goal], 0)])
        fwd_visited = {start: [start]}
        bwd_visited = {goal: [goal]}

        while fwd_queue or bwd_queue:
            if fwd_queue:
                current, path, cost = fwd_queue.popleft()
                metrics.record_node_exploration()
                if current in bwd_visited:
                    full_path = path + bwd_visited[current][-2::-1]
                    metrics.end_timing(full_path)
                    return full_path, metrics
                if len(path) < max_depth:
                    for neighbor, edge_cost in self.get_neighbors(current):
                        if neighbor not in fwd_visited:
                            fwd_visited[neighbor] = path + [neighbor]
                            fwd_queue.append((neighbor, path + [neighbor], cost + edge_cost))

            if bwd_queue:
                current, path, cost = bwd_queue.popleft()
                metrics.record_node_exploration()
                if current in fwd_visited:
                    full_path = fwd_visited[current] + path[-2::-1]
                    metrics.end_timing(full_path)
                    return full_path, metrics
                if len(path) < max_depth:
                    for neighbor, edge_cost in self.get_reverse_neighbors(current):
                        if neighbor not in bwd_visited:
                            bwd_visited[neighbor] = path + [neighbor]
                            bwd_queue.append((neighbor, path + [neighbor], cost + edge_cost))

        metrics.end_timing()
        return [], metrics

    def dijkstra_search(self, start: str, goal: str, max_depth: int = 8):
        metrics = PerformanceMetrics("Dijkstra")
        metrics.start_timing()

        open_set = [(0, start, [start])]
        visited = set()
        distances = {start: 0}

        while open_set:
            current_cost, current, path = heapq.heappop(open_set)
            if current in visited:
                continue
            metrics.record_node_exploration()
            visited.add(current)

            if current == goal:
                metrics.end_timing(path)
                return path, metrics
            if len(path) >= max_depth:
                continue

            for neighbor, edge_cost in self.get_neighbors(current):
                if neighbor in visited:
                    continue
                new_cost = current_cost + edge_cost
                if neighbor not in distances or new_cost < distances[neighbor]:
                    distances[neighbor] = new_cost
                    heapq.heappush(open_set, (new_cost, neighbor, path + [neighbor]))

        metrics.end_timing()
        return [], metrics

    def compare_algorithms(self, start: str, goal: str):
        import datetime
        results = {}
        for name, method in [("A*", self.astar_search),
                              ("Bidirectional", self.bidirectional_search),
                              ("Dijkstra", self.dijkstra_search)]:
            path, metrics = method(start, goal)
            results[name] = {'path': path, 'metrics': metrics.to_dict()}

        successful = {n: d for n, d in results.items() if d['metrics']['path_found']}
        if successful:
            winner_name, winner_data = min(successful.items(),
                                           key=lambda x: x[1]['metrics']['execution_time_ms'])
            winner_info = {
                'algorithm': winner_name,
                'time_ms': winner_data['metrics']['execution_time_ms'],
                'nodes_explored': winner_data['metrics']['nodes_explored']
            }
        else:
            winner_info = {'algorithm': 'None', 'time_ms': 0, 'nodes_explored': 0}

        return {
            'timestamp': datetime.datetime.now().isoformat(),
            'start_emotion': start,
            'goal_emotion': goal,
            'results': results,
            'winner': winner_info
        }
