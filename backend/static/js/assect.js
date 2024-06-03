var assetTable = document.getElementById("assetTable");
var stockTable = document.getElementById("stockTable");


// 在頁面加載時載入數據
window.onload = function () {
    getUserData(assetTable)
        .then(() => {
            loadTableData(assetTable);  // 載入表格數據
        });

    getUserData(stockTable)
        .then(() => {
            loadTableData(stockTable);  // 載入表格數據
        });

};

// 為新增行按鈕添加事件監聽器
document.getElementById("addRowButton").addEventListener("click", function () {
    addRowBeforeSum(assetTable);
});
document.getElementById("addSalaryRowButton").addEventListener("click", function () {
    addRowBeforeSum(stockTable);
});



function getTableData(table) {
    var data = [];
    // 遍歷表格的每一行
    for (var i = 0, row; row = table.rows[i]; i++) {
        var rowData = [];

        // 遍歷行的每一個單元格
        for (var j = 1, col; col = row.cells[j]; j++) {
            // 檢查單元格是否包含輸入欄位
            if (col.children.length > 0 && col.children[0].tagName === "INPUT") {
                // 獲取輸入欄位的值
                rowData.push(col.children[0].value);
            } else {
                // 否則，獲取單元格的文本內容
                rowData.push(col.textContent || col.innerText);
            }
        }
        let data_dict = {};
        data_dict['products'] = rowData[0];
        data_dict['amount'] = rowData[1];
        data_dict['price'] = rowData[2];
        data_dict['date'] = rowData[3];
        // console.log(data_dict);
        data.push(rowData);
    }

    return data;
}

function loadTableData(table) {
    var savedData = localStorage.getItem(table.id + "_tableData");

    if (savedData === null) {
        savedData = [["","","","","",""],["","","","","",""],["","","","","",""]]
    }
    if (savedData) {
        var data = JSON.parse(savedData);
        var currentRowCount = table.rows.length;
        var rowCount = data.length;

        // 根據保存的行數新增行
        for (let i = currentRowCount; i < rowCount; i++) {
            addRowBeforeSum(table);
        }

        // 遍歷表格的每一行
        for (let i = 0, row; row = table.rows[i]; i++) {
            if (data[i] && data[i].length) {
                var rowData = data[i];

                // 遍歷行的每一個單元格
                for (let j = 1, col; col = row.cells[j]; j++) {
                    if (col.children.length > 0 && col.children[0].tagName === "INPUT") {
                        col.children[0].value = rowData[j - 1] || '';
                    } else {
                        col.textContent = rowData[j - 1] || '';
                    }
                }
            }
        }
    }

}


function addRowBeforeSum(table) {
    var newRow = table.insertRow(-1); // 在表格底部插入新行

    // 首先為新行添加一個帶有刪除按鈕的單元格
    var deleteCell = newRow.insertCell(0);
    var deleteButton = document.createElement("button");
    deleteCell.className = 'delete-cell'
    deleteButton.className = "delete-button";

    // 創建並設置 span 元素
    var span = document.createElement("span");
    span.className = "material-icons-sharp";
    span.textContent = "delete_forever";

    // 將 span 添加到按鈕中
    deleteButton.appendChild(span);

    deleteButton.onclick = function () {
        // 點擊按鈕時刪除這一行
        // table.deleteRow(newRow.rowIndex);
        newRow.remove();
        var tableData = getTableData(table);
        localStorage.setItem(table.id + "_tableData", JSON.stringify(tableData));
        // sendUserData(table, tableData);
    };
    deleteCell.appendChild(deleteButton);

    // 依次為新行添加其他單元格
    for (var i = 1; i < 7; i++) {
        var newCell = newRow.insertCell(i); // 注意索引是 i + 1
        var input = document.createElement("input");
        input.type = "text";
        input.readOnly = true;
        if (i === 2) {
            input.className = "input-number";
            input.readOnly = true;
        } else if (i === 3) {
            input.className = "input-number2";
            input.readOnly = true;
        } else if (i === 4) {
            input.type = "date";
            input.className = "input-number3";
            input.readOnly = true;
        } else if (i === 5) {
            input.className = "input-number4";
            input.readOnly = true;  // input 元素添加 readonly 屬性
        } else if (i === 6) {
            input.className = "input-number5";
            input.readOnly = true; 
        }

        newCell.appendChild(input);
    }

}


function getUserData(table) {
    return fetch(`/api/serializer_table_data/${userName}`)
        .then(response => response.json())
        .then(data => {
            const defaultData = [["", "", "", "", "", ""], ["", "", "", "", "", ""], ["", "", "", "", "", ""]];

            if (table.id == 'assetTable') {
                // 如果資料庫沒有該使用者資料 先以 defaultData 代替
                const tableData = data.asset_data === null ? defaultData : data.asset_data;
                localStorage.setItem(table.id + "_tableData", JSON.stringify(tableData));
            } else {
                const tableData = data.stock_data === null ? defaultData : data.stock_data;
                localStorage.setItem(table.id + "_tableData", JSON.stringify(tableData));
            }
        })
        .catch((error) => console.error('Error:', error));
}


