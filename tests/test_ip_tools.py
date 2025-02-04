import unittest
from unittest.mock import patch, mock_open, MagicMock
import subprocess

import ip_tools

class TestIPTool(unittest.TestCase):

    @patch("subprocess.run")
    def test_get_pod_ip_address(self, mock_subprocess):
        """Test extracting pod IPs from 'kubectl get pods' output."""
        mock_subprocess.return_value.stdout = '''
        {
            "items": [
                {
                    "metadata": {"namespace": "default", "name": "pod1"},
                    "status": {"podIP": "192.168.1.10"}
                },
                {
                    "metadata": {"namespace": "kube-system", "name": "pod2"},
                    "status": {"podIP": "10.0.0.5"}
                }
            ]
        }'''

        expected_output = [
            {"namespace": "default", "pod": "pod1", "ip": "192.168.1.10"},
            {"namespace": "kube-system", "pod": "pod2", "ip": "10.0.0.5"},
        ]

        self.assertEqual(ip_tools.get_pod_ip_address(), expected_output)

    @patch('subprocess.run')  # Mock subprocess.run
    def test_called_process_error(self, mock_run):
        # Simulate the CalledProcessError
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,  # Any non-zero return code
            cmd='kubectl get pods --all-namespaces -o json',
            output='Error: Some issue occurred'
        )
        
        # Call the function that invokes subprocess.run
        result = ip_tools.get_pod_ip_address()

        # Assert that the result is an empty list
        self.assertEqual(result, [])

    def test_check_global_collisions_no_collision(self):
        """Test global collision check when no IPs overlap."""
        pod_ips = [
            {"namespace": "default", "pod": "pod1", "ip": "192.168.1.10"},
            {"namespace": "kube-system", "pod": "pod2", "ip": "10.0.0.5"},
        ]
        with patch("builtins.print") as mock_print:
            ip_tools.check_global_collisions(pod_ips)
            mock_print.assert_any_call("No Global IP Collisions Detected")

    def test_check_global_collisions_detected(self):
        """Test global collision check when overlapping subnets exist."""
        pod_ips = [
            {"namespace": "default", "pod": "pod1", "ip": "192.168.1.10"},
            {"namespace": "default", "pod": "pod2", "ip": "192.168.1.20"},
        ]
        with patch("builtins.print") as mock_print:
            ip_tools.check_global_collisions(pod_ips)
            mock_print.assert_any_call("Global IP Collisions Found:")

    def test_check_namespace_collisions_no_collision(self):
        """Test namespace collision check when no overlaps exist in the same namespace."""
        pod_ips = [
            {"namespace": "default", "pod": "pod1", "ip": "192.168.1.10"},
            {"namespace": "kube-system", "pod": "pod2", "ip": "10.0.0.5"},
        ]
        with patch("builtins.print") as mock_print:
            ip_tools.check_namespace_collisions(pod_ips)
            mock_print.assert_any_call("No Namespace-Specific IP Collisions Detected")

    def test_check_namespace_collisions_no_collision(self):
        """Test namespace collision check when no overlaps exist in the same namespace."""
        pod_ips = [
            {"namespace": "default", "pod": "pod1", "ip": "192.168.1.10"},
            {"namespace": "kube-system", "pod": "pod2", "ip": "10.0.0.5"},
        ]
        with patch("builtins.print") as mock_print:
            ip_tools.check_namespace_collisions(pod_ips)
            mock_print.assert_any_call("No Namespace-Specific IP Collisions Detected")

    @patch("builtins.open", new_callable=mock_open, read_data="192.168.1.0/24\n10.0.0.0/8")
    def test_check_collisions_from_file_no_collision(self, mock_file):
        """Test file-based collision check with no overlapping networks."""
        with patch("builtins.print") as mock_print:
            ip_tools.check_collisions_from_file("fake_path.txt")
            mock_print.assert_any_call("No Collisions Found in File")

    @patch("builtins.open", new_callable=mock_open, read_data="192.168.1.0/24\n192.168.1.50/24")
    def test_check_collisions_from_file_detected(self, mock_file):
        """Test file-based collision check with overlapping networks."""
        with patch("builtins.print") as mock_print:
            ip_tools.check_collisions_from_file("fake_path.txt")
            mock_print.assert_any_call("Collisions Found in File:")

    @patch('builtins.open', side_effect=FileNotFoundError)  # Mock open to raise FileNotFoundError
    def test_file_not_found(self, mock_open):
        file_path = "non_existent_file.txt"  # File that does not exist

        # Call the function that will raise the FileNotFoundError
        result = ip_tools.check_collisions_from_file(file_path)

        # Assert that an empty list (or any appropriate value) is returned
        self.assertIsNone(result)  # Adjust based on your actual return value


if __name__ == '__main__':
    unittest.main()