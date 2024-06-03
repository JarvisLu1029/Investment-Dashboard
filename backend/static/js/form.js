document.getElementById("editAsset").addEventListener("click", function (e) {
	editColumn(this);
});
document.getElementById("editStock").addEventListener("click", function (e) {
	editColumn(this);
});


function sendUserData(table) {
	var userData = getTableData(table);
	const data = table.id == 'assetTable' ? { 'user': userName, 'asset_data': userData } : { 'user': userName, 'stock_data': userData };
	return postData(`/api/serializer_table_data/${userName}`, data);
}

// 修改 postData 函數以返回一個 Promise
function postData(url, data) {
	return fetch(url, { // 確保返回 fetch 的 Promise
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify(data)
	})
		.then(response => response.json())
		.catch((error) => console.error('Error:', error));
}


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


function editColumn(element) {
    var iconSpan = element.querySelector('.material-icons-sharp');
    var inputs = element.closest('tbody').querySelectorAll('input');
    var tbody = element.closest('tbody');
    var secondRow = tbody.querySelectorAll('tr')[1]; // 獲取第二個 tr
    var targetTd = secondRow.querySelectorAll('td')[0]; // 在第二個 tr 中找到第一個 td
    

	var deleteElements = tbody.querySelectorAll('.delete-button');

    // 判斷當前模式是編輯還是保存
    if (iconSpan.innerHTML === 'edit') {
		deleteElements.forEach(function(element) {
			element.style.display = 'block';
		});
		
        iconSpan.innerHTML = 'save'; // 切換圖標
        inputs.forEach(input => input.removeAttribute('readonly')); // 啟用編輯
        
        // 如果已經有 addButton，則不再重複添加
        var existingAddButton = targetTd.querySelector('.add-row-button');
        if (!existingAddButton) {
            var addButton = document.createElement('button');
            addButton.className = 'add-row-button';
            var span = document.createElement("span");
            span.className = "material-icons-sharp";
            span.textContent = "add";
            addButton.appendChild(span);

            // 將 addButton 添加到目標 td 中
            targetTd.appendChild(addButton);

            // 為 addButton 添加事件處理器
            addButton.addEventListener('click', function(event) {
                addRow(tbody);
                event.stopPropagation(); // 阻止事件冒泡
            });
        }
    } else {
        iconSpan.innerHTML = 'edit'; // 切換圖標

		deleteElements.forEach(function(element) {
			element.style.display = 'none';
		});
		
        inputs.forEach(input => input.setAttribute('readonly', true)); // 禁用編輯
		
		var userData = getTableData(tbody)
		console.log(userData);
		sendUserData(tbody);

        // 移除 addButton
        var addButton = targetTd.querySelector('.add-row-button');
        if (addButton) {
            targetTd.removeChild(addButton);
        }
    }
}


function addRow(table) {
	console.log(table)
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
		sendUserData(table);
	};
	deleteCell.appendChild(deleteButton);

	// 依次為新行添加其他單元格
	for (var i = 1; i < 7; i++) {
		var newCell = newRow.insertCell(i); // 注意索引是 i + 1
		var input = document.createElement("input");
		input.type = "text";
		if (i === 2) {
			input.className = "input-number";
		} else if (i === 3) {
			input.className = "input-number2";
		} else if (i === 4) {
			input.type = "date";
			input.className = "input-number3";
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