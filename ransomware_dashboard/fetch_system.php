<?php
header('Content-Type: application/json');

// CPU Usage
$cpuLoad = sys_getloadavg();
$cpu = round(($cpuLoad[0] / (int) shell_exec("nproc")) * 100);

// RAM Usage
$free = shell_exec('free');
preg_match('/Mem:\s+(\d+)\s+(\d+)/', $free, $matches);
$ramTotal = $matches[1];
$ramUsed = $matches[2];
$ram = round(($ramUsed / $ramTotal) * 100);

// Disk Usage
$df = disk_free_space("/");
$dt = disk_total_space("/");
$disk = round((($dt - $df) / $dt) * 100);

// Network Activity (Simulated)
$net = rand(10, 80); // Replace with actual ifconfig parsing if needed

echo json_encode([
  'cpu' => $cpu,
  'ram' => $ram,
  'disk' => $disk,
  'net' => $net
]);
