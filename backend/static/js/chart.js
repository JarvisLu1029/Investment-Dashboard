function createTotalInvestmentChart(totalAsset, totalStock) {
    const ctx = document.getElementById('myChart').getContext('2d');

    var totalAssetPercent = ((totalAsset / (totalAsset + totalStock)) * 100).toFixed(0)
    var totalStockPercent = 100 - totalAssetPercent

    document.querySelector('.status .percentage p').textContent = `${totalStockPercent}% / ${totalAssetPercent}%`;

    const myChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                label: '我的第一個圓餅圖',
                data: [0, totalAsset, totalStock],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                borderWidth: 0.3
            }]
        },
        options: {
            responsive: false
        }
    });
}


function extractNumber(str) {
    var numericPart = str.replace(/[^0-9]/g, ''); // 移除非數字字符
    return parseInt(numericPart);
}


function createTotalProfitChart(totalInvestmentNum, totalProfitNum) {
    const profitLoss = document.getElementById('profitLossChart').getContext('2d');
    document.getElementById('total-investment').textContent = `$ ${totalInvestmentNum}`;
    document.getElementById('total-profit').textContent = `$ ${totalProfitNum}`;

    var totalProfitTextContent = ((totalProfitNum / totalInvestmentNum) * 100).toFixed(1);
    var totalProfitBackgroundColor;

    if (totalProfitNum < 0) {
        document.querySelector('.visits .percentage p').textContent = `${totalProfitTextContent}%`;
        totalProfitBackgroundColor = 'rgba(255, 99, 132, 0.2)';
    } else {
        document.querySelector('.visits .percentage p').textContent = `${totalProfitTextContent}%`;
        totalProfitBackgroundColor = 'rgba(255, 206, 86, 0.2)';
    }

    const profitLossChart = new Chart(profitLoss, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [Math.abs(totalProfitNum), totalInvestmentNum - Math.abs(totalProfitNum)],
                backgroundColor: [
                    totalProfitBackgroundColor,
                    'rgba(54, 162, 235, 0.2)',
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                ],
                borderWidth: 0.3
            }]
        },
        options: {
            responsive: false
        }
    });
}


function populateSelect(options) {
    const selectElement = document.getElementById('dynamicSelect');
    options = options.data
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option;
        optionElement.textContent = option;
        selectElement.appendChild(optionElement);
    });
}


// 假設您有一個全局變量來存儲圖表實例
let myChart = null;
function executeApi(selectedValue) {
    // 如果已經有一個圖表實例，先銷毀它
    if (myChart) {
        myChart.destroy();
    }
    fetch(`/api/investment_price/${selectedValue}`)
        .then(response => response.json())
        .then(data => {
            // 在這裡，data變量將包含您的API返回的資料
            var ctx = document.getElementById('lineChartPrice').getContext('2d'); // 確保您有一個<canvas>元素的ID為'lineChart'

            var config = {
                type: 'line',
                data: {
                    labels: data.create_time, // 使用API返回的標籤
                    datasets: [{
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 2,
                        label: 'Price',
                        data: data.price, // 使用API返回的資料
                        fill: false,
                        pointStyle: 'rect',
                        pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    }]
                },
                options: {
                    legend: {
                        labels: {
                            fontColor: '#333333'
                        }
                    },
                    scales: {
                        x: {
                            gridLines: {
                                color: '#eeeeee'
                            },
                            ticks: {
                                color: "#CCC" // 'fontColor' 改為 'color'
                            },
                        },
                        y: {
                            gridLines: {
                                color: '#eeeeee'
                            },
                            ticks: {
                                color: "#CCC",
                                beginAtZero: true,
                            },
                        }
                    }
                }
            };
            myChart = new Chart(ctx, config);
        }
        )
};

fetch(`/api/doughnut_profit_chart/${userName}`)
    .then(response => response.json())
    .then(data => {
        createTotalProfitChart(data.total_investment, data.profit)
        createTotalInvestmentChart(data.total_asset, data.total_stock)
    })


fetch(`/api/investment_list/${userName}`)
    .then(response => response.json())
    .then(data => {
        populateSelect(data)

        // 當文件加載完成後，立即執行預設選項的API調用
        executeApi(document.getElementById('dynamicSelect').value);
        document.getElementById('dynamicSelect').addEventListener('change', function () {
            // 當選擇的選項改變時，執行相應的API調用
            executeApi(this.value);
        });

    })


fetch(`/api/line_profit_chart/${userName}`)
    .then(response => response.json())
    .then(data => {
        var ctx = document.getElementById('lineChart').getContext('2d');
        var config = {
            type: 'line',
            data: {
                labels: data.date, // 使用API返回的標籤
                datasets: [{
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    label: 'Profit & Loss',
                    data: data.profit, // 使用API返回的資料
                    fill: false,
                    pointStyle: 'rect',
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                }]
            },
            options: {
                legend: {
                    labels: {
                        fontColor: '#333333'
                    }
                },
                scales: {
                    x: {
                        gridLines: {
                            color: '#eeeeee'
                        },
                        ticks: {
                            color: "#CCC", // 'fontColor' 改為 'color'
                        },
                    },
                    y: {
                        gridLines: {
                            color: '#eeeeee'
                        },
                        ticks: {
                            color: "#CCC",
                            stepSize: 1000
                            // beginAtZero: true
                        },
                    }
                }
            }
        };
        new Chart(ctx, config);
    })
    .catch(error => console.error('Fetching data failed:', error));



