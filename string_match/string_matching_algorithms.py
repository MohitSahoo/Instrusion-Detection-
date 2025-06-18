# string_matching_algorithms.py

import time
import random
from typing import List, Dict, Any, Tuple

class StringMatchingAlgorithms:
    """
    A suite of string matching algorithms with visualization and performance analysis.
    """

    def __init__(self):
        self.algorithms = {
            'naive': self.naive_search,
            'boyer_moore': self.boyer_moore_search,
            'horspool': self.horspool_search
        }
        self.results = {}

    def _capture_frame(self, visualize: bool, frame_data: Dict[str, Any], visualization_frames: List[Dict[str, Any]]) -> None:
        """Captures a frame of the algorithm's execution for visualization."""
        if not visualize:
            return

        # Ensure frame_data is a dictionary
        if not isinstance(frame_data, dict):
            print(f"Warning: Invalid frame data type: {type(frame_data)}")
            return

        # Ensure required fields are present
        required_fields = ['type', 'message']
        for field in required_fields:
            if field not in frame_data:
                print(f"Warning: Missing required field '{field}' in frame data")
                return

        # Ensure visualization_frames is a list
        if not isinstance(visualization_frames, list):
            print("Warning: visualization_frames is not a list")
            return

        # Add frame to visualization frames
        visualization_frames.append(frame_data)

    def naive_search(self, text: str, pattern: str, visualize: bool = False) -> Dict[str, Any]:
        n = len(text)
        m = len(pattern)
        matches = []
        visualization_frames = []
        # comparisons = 0 # Removed for no complexity display

        if m == 0: return {'matches': [], 'visualization_frames': []} #, 'comparisons': 0}
        if n == 0 or n < m: return {'matches': [], 'visualization_frames': []} #, 'comparisons': 0}

        for i in range(n - m + 1):
            self._capture_frame(visualize, {
                'type': 'alignment',
                'text': text,
                'pattern': pattern,
                'text_idx': i,
                'pattern_idx': 0,
                'current_window': text[i:i+m],
                'message': f"Aligning pattern at text index {i}",
                'matches': list(matches)
            }, visualization_frames)

            j = 0
            while j < m:
                # comparisons += 1 # Removed for no complexity display
                self._capture_frame(visualize, {
                    'type': 'comparison',
                    'text': text,
                    'pattern': pattern,
                    'text_idx': i,
                    'pattern_idx': j,
                    'match_status': (text[i+j] == pattern[j]),
                    'current_window': text[i:i+m],
                    'message': f"Comparing text[{i+j}] ('{text[i+j]}') with pattern[{j}] ('{pattern[j]}')",
                    'matches': list(matches)
                }, visualization_frames)
                if text[i + j] != pattern[j]:
                    self._capture_frame(visualize, {
                        'type': 'mismatch',
                        'text': text,
                        'pattern': pattern,
                        'text_idx': i,
                        'pattern_idx': j,
                        'current_window': text[i:i+m],
                        'message': f"Mismatch! Shifting pattern by 1.",
                        'matches': list(matches)
                    }, visualization_frames)
                    break
                j += 1

            if j == m:
                matches.append(i)
                self._capture_frame(visualize, {
                    'type': 'match',
                    'text': text,
                    'pattern': pattern,
                    'text_idx': i,
                    'pattern_idx': 0,
                    'current_window': text[i:i+m],
                    'message': f"Match found at index {i}!",
                    'matches': list(matches)
                }, visualization_frames)
        return {'matches': matches, 'visualization_frames': visualization_frames} #, 'comparisons': comparisons}

    def boyer_moore_search(self, text: str, pattern: str, visualize: bool = False) -> Dict[str, Any]:
        n = len(text)
        m = len(pattern)
        matches = []
        visualization_frames = []
        # comparisons = 0 # Removed

        if m == 0: return {'matches': [], 'visualization_frames': []} #, 'comparisons': 0}
        if n == 0 or n < m: return {'matches': [], 'visualization_frames': []} #, 'comparisons': 0}

        # Build bad character table
        bad_char_table = self._build_bad_char_table(pattern, visualize, visualization_frames)
        
        s = 0  # s is shift of the pattern with respect to text
        while s <= n - m:
            self._capture_frame(visualize, {
                'type': 'alignment',
                'text': text,
                'pattern': pattern,
                'text_idx': s,
                'pattern_idx': 0,
                'current_window': text[s:s+m],
                'bad_char_table': bad_char_table,
                'message': f"Aligning pattern at text index {s}",
                'matches': list(matches)
            }, visualization_frames)

            j = m - 1  # Start from rightmost character of pattern
            while j >= 0:
                # comparisons += 1 # Removed
                self._capture_frame(visualize, {
                    'type': 'comparison',
                    'text': text,
                    'pattern': pattern,
                    'text_idx': s + j,
                    'pattern_idx': j,
                    'match_status': (pattern[j] == text[s + j]),
                    'bad_char_table': bad_char_table,
                    'message': f"Comparing text[{s+j}] ('{text[s+j]}') with pattern[{j}] ('{pattern[j]}')",
                    'matches': list(matches)
                }, visualization_frames)

                if pattern[j] != text[s + j]:
                    # Get the shift from bad character table
                    shift = bad_char_table.get(text[s + j], -1)
                    shift_amount = max(1, j - shift)
                    
                    self._capture_frame(visualize, {
                        'type': 'mismatch_shift',
                        'text': text,
                        'pattern': pattern,
                        'text_idx': s + j,
                        'pattern_idx': j,
                        'bad_char_table': bad_char_table,
                        'shift_amount': shift_amount,
                        'message': f"Mismatch! Shifting pattern by {shift_amount} using bad character rule",
                        'matches': list(matches)
                    }, visualization_frames)
                    
                    s += shift_amount
                    break
                j -= 1

            if j < 0:  # Pattern found
                matches.append(s)
                self._capture_frame(visualize, {
                    'type': 'match',
                    'text': text,
                    'pattern': pattern,
                    'text_idx': s,
                    'pattern_idx': 0,
                    'bad_char_table': bad_char_table,
                    'message': f"Match found at index {s}!",
                    'matches': list(matches)
                }, visualization_frames)
                s += 1  # Shift by 1 to find next match
        return {'matches': matches, 'visualization_frames': visualization_frames} #, 'comparisons': comparisons}

    def _build_bad_char_table(self, pattern: str, visualize: bool, visualization_frames: List[Dict[str, Any]]) -> Dict[str, int]:
        m = len(pattern)
        bad_char_table = {}
        for i in range(m - 1): # Last character doesn't participate in shift calculation for itself
            bad_char_table[pattern[i]] = i
        
        self._capture_frame(visualize, {
            'type': 'bad_char_table',
            'pattern': pattern,
            'bad_char_table': bad_char_table,
            'message': "Built Bad Character Table: stores last occurrence of each char in pattern (excluding last char).",
            'current_i': None
        }, visualization_frames)
        return bad_char_table

    def horspool_search(self, text: str, pattern: str, visualize: bool = False) -> Dict[str, Any]:
        n = len(text)
        m = len(pattern)
        matches = []
        visualization_frames = []
        # comparisons = 0 # Removed
        # shifts = 0 # Removed

        if m == 0: return {'matches': [], 'visualization_frames': []} #, 'comparisons': 0, 'shifts': 0}
        if n == 0 or n < m: return {'matches': [], 'visualization_frames': []} #, 'comparisons': 0, 'shifts': 0}

        # Build the shift table
        shift_table = {}
        for i in range(256): # Initialize with pattern length for all possible ASCII chars
            shift_table[chr(i)] = m
        for i in range(m - 1):
            shift_table[pattern[i]] = m - 1 - i

        self._capture_frame(visualize, {
            'type': 'shift_table',
            'pattern': pattern,
            'shift_table': {k:v for k,v in shift_table.items() if v != m}, # Show relevant entries
            'message': "Built Shift Table (similar to Bad Character Rule but simpler)."
        }, visualization_frames)

        s = 0  # s is shift of the pattern with respect to text
        while s <= n - m:
            j = m - 1  # Start matching from the end of the pattern
            
            self._capture_frame(visualize, {
                'type': 'alignment',
                'text': text,
                'pattern': pattern,
                'text_idx': s,
                'pattern_idx': 0,
                'current_window': text[s:s+m],
                'shift_table': {k:v for k,v in shift_table.items() if v != m},
                'message': f"Aligning pattern at text index {s}. Starting comparison from right.",
                'matches': list(matches)
            }, visualization_frames)

            while j >= 0:
                # comparisons += 1 # Removed
                self._capture_frame(visualize, {
                    'type': 'comparison',
                    'text': text,
                    'pattern': pattern,
                    'text_idx': s + j,
                    'pattern_idx': j,
                    'match_status': (text[s + j] == pattern[j]),
                    'current_window': text[s:s+m],
                    'shift_table': {k:v for k,v in shift_table.items() if v != m},
                    'message': f"Comparing text[{s+j}] ('{text[s+j]}') with pattern[{j}] ('{pattern[j]}')",
                    'matches': list(matches)
                }, visualization_frames)
                if pattern[j] != text[s + j]:
                    break
                j -= 1

            if j < 0: # Pattern found
                matches.append(s)
                self._capture_frame(visualize, {
                    'type': 'match',
                    'text': text,
                    'pattern': pattern,
                    'text_idx': s,
                    'pattern_idx': 0,
                    'current_window': text[s:s+m],
                    'shift_table': {k:v for k,v in shift_table.items() if v != m},
                    'message': f"Match found at index {s}!",
                    'matches': list(matches)
                }, visualization_frames)
                
                # Shift by the shift table value for the character immediately after the match
                shift_val = shift_table.get(text[s + m] if s + m < n else '', m)
                # shifts += 1 # Removed
                self._capture_frame(visualize, {
                    'type': 'shift',
                    'text': text,
                    'pattern': pattern,
                    'text_idx': s, # Old alignment
                    'next_char_idx': s + m, # Index of the character after the window
                    'shift_amount': shift_val,
                    'message': f"Match. Shifting pattern by {shift_val} based on char '{text[s+m] if s+m < n else 'End of Text'}'",
                    'matches': list(matches)
                }, visualization_frames)
                s += shift_val
            else: # Mismatch
                # Character that caused mismatch in text
                mismatched_char = text[s + m - 1] 
                shift_val = shift_table.get(mismatched_char, m)
                # shifts += 1 # Removed
                self._capture_frame(visualize, {
                    'type': 'shift',
                    'text': text,
                    'pattern': pattern,
                    'text_idx': s, # Old alignment
                    'mismatched_char_idx': s + m - 1, # Index of character causing mismatch
                    'mismatched_char': mismatched_char,
                    'shift_amount': shift_val,
                    'message': f"Mismatch at text[{s+j}] ('{text[s+j]}'). Shifting pattern by {shift_val} based on '{mismatched_char}'.",
                    'matches': list(matches)
                }, visualization_frames)
                s += shift_val
        return {'matches': matches, 'visualization_frames': visualization_frames} #, 'comparisons': comparisons, 'shifts': shifts}

    def run_algorithm(self, algorithm: str, text: str, pattern: str, visualize: bool = False) -> Dict[str, Any]:
        """Runs the specified algorithm and returns the results."""
        if algorithm not in self.algorithms:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        start_time = time.time()
        try:
            result = self.algorithms[algorithm](text, pattern, visualize)
            
            # Validate result structure
            if not isinstance(result, dict):
                raise ValueError(f"Algorithm {algorithm} returned invalid result type: {type(result)}")
            
            # Ensure required fields
            if 'matches' not in result:
                result['matches'] = []
            if 'visualization_frames' not in result:
                result['visualization_frames'] = []
            
            # Ensure matches is a list
            if not isinstance(result['matches'], list):
                result['matches'] = []
            
            # Ensure visualization_frames is a list
            if not isinstance(result['visualization_frames'], list):
                result['visualization_frames'] = []
            
            end_time = time.time()
            result['algorithm'] = algorithm
            result['execution_time'] = end_time - start_time
            return result
            
        except Exception as e:
            end_time = time.time()
            # Return a valid result structure even in case of error
            return {
                'algorithm': algorithm,
                'matches': [],
                'visualization_frames': [],
                'execution_time': end_time - start_time,
                'error': str(e)
            }

    def compare_algorithms(self, text: str, pattern: str, algorithms: List[str] = None) -> Dict[str, Dict[str, Any]]:
        if algorithms is None:
            algorithms = list(self.algorithms.keys())
        
        results = {}
        for algo in algorithms:
            if algo in self.algorithms:
                results[algo] = self.run_algorithm(algo, text, pattern)
        return results

    def benchmark_algorithms(self, text_sizes: List[int] = None, pattern_size: int = 5,
                           num_trials: int = 10) -> Tuple[Dict[str, List[float]], List[int]]:
        if text_sizes is None:
            text_sizes = [100, 500, 1000, 2000, 5000, 10000]
        
        results = {algo: [] for algo in self.algorithms}
        valid_sizes = []
        
        for size in text_sizes:
            # Generate random text and pattern
            text = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=size))
            pattern = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=pattern_size))
            
            # Run each algorithm multiple times
            for algo in self.algorithms:
                times = []
                for _ in range(num_trials):
                    start_time = time.time()
                    self.algorithms[algo](text, pattern)
                    end_time = time.time()
                    times.append(end_time - start_time)
                
                # Use median time to avoid outliers
                median_time = sorted(times)[num_trials // 2]
                results[algo].append(median_time)
            
            valid_sizes.append(size)
        
        return results, valid_sizes