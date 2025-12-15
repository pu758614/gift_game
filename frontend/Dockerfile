FROM node:18-alpine

WORKDIR /app

# 複製 package 檔案
COPY package*.json ./

# 安裝依賴
RUN npm install

# 複製所有檔案
COPY . .

# 暴露端口
EXPOSE 3000

# 啟動開發伺服器
CMD ["npm", "run", "dev", "--", "--host"]
