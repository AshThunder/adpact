import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

function xProfilePlugin() {
  return {
    name: 'x-profile-proxy',
    configureServer(server) {
      server.middlewares.use('/api/x-profile', async (req, res) => {
        // Strip query string and leading slashes/ats
        const rawHandle = req.url.split('?')[0].replace(/^\/+/, '').replace(/@/g, '').trim();
        if (!rawHandle) {
          res.statusCode = 400;
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({ exists: false, error: 'Missing handle' }));
          return;
        }

        try {
          const fxRes = await fetch(`https://api.fxtwitter.com/${rawHandle}`, {
            redirect: 'manual',
            headers: {
              'User-Agent': 'Mozilla/5.0 (compatible; AdPact/1.0; +https://adpact.io)'
            }
          });

          if (fxRes.status === 200) {
            const data = await fxRes.json();
            if (data.code === 200 && data.user) {
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({
                exists: true,
                handle: data.user.screen_name,
                displayName: data.user.name,
                avatarUrl: data.user.avatar_url,
                followers: data.user.followers,
                following: data.user.following,
                description: data.user.description,
                verified: !!data.user.verification?.verified
              }));
              return;
            }
          }

          // 302 or 404 indicates non-existent account
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({
            exists: false,
            error: `@${rawHandle} does not exist on X`
          }));
        } catch (err) {
          console.error('[x-profile-proxy] Error fetching profile:', err.message);
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({
            exists: false,
            error: 'Could not connect to X service'
          }));
        }
      });

      server.middlewares.use('/api/x-tweet', async (req, res) => {
        const parts = req.url.split('?')[0].replace(/^\/+/, '').split('/');
        const handle = parts[0]?.replace(/@/g, '').trim();
        const tweetId = parts[1]?.trim();

        if (!handle || !tweetId) {
          res.statusCode = 400;
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({ success: false, error: 'Missing handle or tweetId' }));
          return;
        }

        try {
          const fxRes = await fetch(`https://api.fxtwitter.com/${handle}/status/${tweetId}`, {
            redirect: 'manual',
            headers: {
              'User-Agent': 'Mozilla/5.0 (compatible; AdPact/1.0; +https://adpact.io)'
            }
          });

          if (fxRes.status === 200) {
            const data = await fxRes.json();
            if (data.code === 200 && data.tweet) {
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({
                success: true,
                id: data.tweet.id,
                text: data.tweet.text || '',
                author: data.tweet.author?.screen_name || '',
                url: data.tweet.url || ''
              }));
              return;
            }
          }

          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({
            success: false,
            error: 'Tweet not found on X'
          }));
        } catch (err) {
          console.error('[x-tweet-proxy] Error fetching tweet:', err.message);
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({
            success: false,
            error: 'Could not connect to X service'
          }));
        }
      });
    }
  };
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), xProfilePlugin()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('vue')) {
              return 'vendor-vue';
            }
            if (id.includes('ethers') || id.includes('genlayer')) {
              return 'vendor-web3';
            }
            return 'vendor';
          }
        }
      }
    }
  }
})
