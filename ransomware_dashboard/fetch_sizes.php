<?php
header('Content-Type: application/json');

function getFolderSize($dir) {
    $size = 0;
    foreach (new RecursiveIteratorIterator(new RecursiveDirectoryIterator($dir)) as $file) {
        if ($file->isFile()) {
            $size += $file->getSize();
        }
    }
    return $size;
}

echo json_encode([
    "data" => round(getFolderSize("/home/aniket/Desktop/Projects/cloud_ransomware_recovery/data") / (1024 * 1024), 2),
    "quarantine" => round(getFolderSize("/home/aniket/Desktop/Projects/cloud_ransomware_recovery/quarantine") / (1024 * 1024), 2),
    "backup" => round(getFolderSize("/home/aniket/Desktop/Projects/cloud_ransomware_recovery/backups") / (1024 * 1024), 2)
]);
