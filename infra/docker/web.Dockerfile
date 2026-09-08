FROM node:22-alpine AS build
WORKDIR /app
COPY apps/web/package*.json ./
RUN npm install
COPY apps/web .
RUN npm run build

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup -S pipe4 && adduser -S pipe4 -G pipe4
COPY --from=build --chown=pipe4:pipe4 /app/build ./build
COPY --from=build --chown=pipe4:pipe4 /app/package.json ./package.json
COPY --from=build --chown=pipe4:pipe4 /app/node_modules ./node_modules
USER pipe4
EXPOSE 3000
CMD ["node", "build"]
