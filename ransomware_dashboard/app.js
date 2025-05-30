let diskChart = null;

function fetchUpdates() {
  fetch('fetch_data.php')
    .then(response => response.json())
    .then(data => {
      updateFolderView('dataContent', data.data);
      updateFolderView('quarantineContent', data.quarantine);
      updateFolderView('backupContent', data.backup);
      checkNewAlerts(data.log);

      // Update badge counts
      document.getElementById("dataBadge").innerText = data.data.length;
      document.getElementById("quarantineBadge").innerText = data.quarantine.length;
      document.getElementById("backupBadge").innerText = data.backup.length;

      updateDiskChart(data.data.length, data.quarantine.length, data.backup.length);

      // Animate new cards
      gsap.from('.card', {
        opacity: 0,
        y: 20,
        duration: 0.5,
        stagger: 0.1,
        ease: "power2.out"
      });
    });
}

function updateFolderView(elementId, items) {
  const element = document.getElementById(elementId);

  if (!items || items.length === 0) {
    element.innerHTML = '<p>No files found.</p>';
    return;
  }

  const existingItems = Array.from(element.querySelectorAll('li')).map(li => li.textContent);
  const listItems = [];

  items.forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;

    // Animate new items
    if (!existingItems.includes(item)) {
      gsap.fromTo(li, 
        { backgroundColor: "#00ffcc22", scale: 1.05 },
        { backgroundColor: "transparent", scale: 1, duration: 1, ease: "power2.out" }
      );
    }

    listItems.push(li);
  });

  element.innerHTML = '';
  const ul = document.createElement('ul');
  listItems.forEach(li => ul.appendChild(li));
  element.appendChild(ul);
}

let lastShown = new Set();

const importantKeywords = [
  {
    match: line => line.includes("Backup created and encrypted"),
    type: "success",
    icon: "✅",
    label: "Backup created"
  },
  {
    match: line => line.includes("[THREAT] Suspicious encrypted file detected"),
    type: "warning",
    icon: "🚨",
    label: "Suspicious file found"
  },
  {
    match: line => line.includes("[QUARANTINE] Data zipped and moved to quarantine"),
    type: "info",
    icon: "🧰",
    label: "Data moved to quarantine"
  },
  {
    match: line => line.includes("[RESTORE] Restored from"),
    type: "info",
    icon: "🔁",
    label: "Restored from backup"
  }
];

function checkNewAlerts(logs) {
  const container = document.getElementById('notificationContainer');

  logs.forEach(logLine => {
    importantKeywords.forEach(({ match, type, icon, label }) => {
      if (match(logLine) && !lastShown.has(logLine)) {
        lastShown.add(logLine);

        const alert = document.createElement('div');
        alert.className = `notification ${type}`;
        alert.innerHTML = `<span class="icon">${icon}</span> <strong>${label}</strong><br><span class="log-line">${logLine}</span>`;

        container.prepend(alert);

        gsap.to(alert, { duration: 0.5, opacity: 1, y: 0, ease: "power2.out" });

        setTimeout(() => {
          gsap.to(alert, {
            duration: 0.5,
            opacity: 0,
            y: -20,
            ease: "power2.in",
            onComplete: () => alert.remove()
          });
        }, 10000);
      }
    });
  });

  if (lastShown.size > 100) {
    lastShown = new Set(Array.from(lastShown).slice(-50));
  }
}

document.getElementById('themeToggle').addEventListener('click', () => {
  document.body.classList.toggle('light-mode');
});

document.querySelectorAll('.folder-header').forEach(header => {
  header.style.cursor = 'pointer';
  header.addEventListener('click', () => {
    const targetId = header.getAttribute('data-target');
    const content = document.getElementById(targetId);
    const toggleIcon = header.querySelector('.toggle-icon');

    if (content.style.display === 'none') {
      content.style.display = 'block';
      toggleIcon.textContent = '▼';
    } else {
      content.style.display = 'none';
      toggleIcon.textContent = '▶';
    }
  });
});

['dataContent', 'quarantineContent', 'backupContent'].forEach(id => {
  document.getElementById(id).style.display = 'block';
});

setInterval(fetchUpdates, 3000);
fetchUpdates();

function updateSystemHealth() {
  fetch('fetch_system.php')
    .then(res => res.json())
    .then(data => {
      document.getElementById('cpuBar').style.width = `${data.cpu}%`;
      document.getElementById('ramBar').style.width = `${data.ram}%`;
      document.getElementById('diskBar').style.width = `${data.disk}%`;
      document.getElementById('netBar').style.width = `${data.net}%`;
    });
}

setInterval(updateSystemHealth, 5000);
updateSystemHealth();

document.querySelectorAll(".toggle-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const target = document.getElementById(btn.dataset.target);
    const isCollapsed = target.style.maxHeight === "0px";
    target.style.maxHeight = isCollapsed ? "500px" : "0px";
    btn.innerText = isCollapsed ? "▼" : "▲";
  });
});

function updateDiskChart(dataCount, quarantineCount, backupCount) {
  const ctx = document.getElementById('diskChart').getContext('2d');

  const chartData = {
    labels: ['Data', 'Quarantine', 'Backups'],
    datasets: [{
      data: [dataCount, quarantineCount, backupCount],
      backgroundColor: ['#00ffc8', '#ff6363', '#5f72ff'],
      borderWidth: 0
    }]
  };

  const config = {
    type: 'doughnut',
    data: chartData,
    options: {
      responsive: false,
      cutout: '60%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: getComputedStyle(document.body).getPropertyValue('--text-color') || '#fff'
          }
        }
      }
    }
  };

  if (diskChart) {
    diskChart.data = chartData;
    diskChart.update();
  } else {
    diskChart = new Chart(ctx, config);
  }
}
