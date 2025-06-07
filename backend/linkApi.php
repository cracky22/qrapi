<?php
header('Content-Type: application/json');

$jsonFile = 'links.json';

if (!file_exists($jsonFile)) {
    file_put_contents($jsonFile, json_encode([]));
}

function loadLinks() {
    global $jsonFile;
    return json_decode(file_get_contents($jsonFile), true) ?: [];
}

function saveLinks($links) {
    global $jsonFile;
    file_put_contents($jsonFile, json_encode($links, JSON_PRETTY_PRINT));
}

function generateLinkID() {
    return substr(md5(uniqid(rand(), true)), 0, 8);
}

function validateDate($date) {
    return DateTime::createFromFormat('Y-m-d,H:i', $date) !== false;
}

function isExpired($expire) {
    $expireDate = new DateTime($expire);
    $now = new DateTime();
    return $now > $expireDate;
}

function cleanExpiredLinks() {
    $links = loadLinks();
    $updatedLinks = array_filter($links, function($link) {
        return !isExpired($link['expire']);
    });
    if (count($links) !== count($updatedLinks)) {
        saveLinks($updatedLinks);
    }
    return $updatedLinks;
}

$action = isset($_GET['action']) ? $_GET['action'] : '';

$links = cleanExpiredLinks();

if ($action === 'create') {
    $link = isset($_GET['link']) ? filter_var($_GET['link'], FILTER_VALIDATE_URL) : '';
    $expire = isset($_GET['expire']) ? $_GET['expire'] : '';

    if (!$link || !$expire || !validateDate($expire)) {
        http_response_code(400);
        echo json_encode(['error' => 'Invalid URL or expiration date']);
        exit;
    }

    $linkID = generateLinkID();
    $links[$linkID] = [
        'url' => $link,
        'expire' => $expire
    ];

    saveLinks($links);
    echo json_encode(['linkID' => $linkID]);
} elseif ($action === 'open') {
    $linkID = isset($_GET['linkID']) ? $_GET['linkID'] : '';

    if (!$linkID) {
        http_response_code(400);
        echo json_encode(['error' => 'Missing linkID']);
        exit;
    }

    if (isset($links[$linkID])) {
        if (isExpired($links[$linkID]['expire'])) {
            http_response_code(410);
            echo json_encode(['error' => 'Link has expired']);
        } else {
            header('Location: ' . $links[$linkID]['url']);
            exit;
        }
    } else {
        http_response_code(404);
        echo json_encode(['error' => 'Link not found']);
    }
} else {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid action']);
}
?>