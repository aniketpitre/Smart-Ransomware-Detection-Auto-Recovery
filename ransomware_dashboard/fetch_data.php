<?php
header('Content-Type: application/json');

// Absolute paths to your folders
$dataFolder = '/home/aniket/Desktop/Projects/cloud_ransomware_recovery/data';
$quarantineFolder = '/home/aniket/Desktop/Projects/cloud_ransomware_recovery/quarantine';
$backupFolder = '/home/aniket/Desktop/Projects/cloud_ransomware_recovery/backups';
$logFile = '/home/aniket/Desktop/Projects/cloud_ransomware_recovery/logs/activity.log';

// Get files inside a folder (excluding '.' and '..')
function getFolderContents($folderPath) {
    if (!is_dir($folderPath)) {
        return [];
    }
    $files = scandir($folderPath);
    return array_values(array_diff($files, ['.', '..']));
}

// Read last N lines of the log file
function getLogContents($filePath, $lines = 50) {
    if (!file_exists($filePath)) {
        return [];
    }
    $file = file($filePath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    return array_slice(array_reverse($file), 0, $lines);
}

$response = [
    'data' => getFolderContents($dataFolder),
    'quarantine' => getFolderContents($quarantineFolder),
    'backup' => getFolderContents($backupFolder),
    'log' => getLogContents($logFile)
];

// Output JSON response
echo json_encode($response /*, JSON_PRETTY_PRINT */);
