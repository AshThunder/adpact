const puppeteer = require('puppeteer-core');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const scenes = JSON.parse(fs.readFileSync('demo_assets/scenes.json', 'utf8'));
const FPS = 25;

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function renderSceneFrames(page, scene, frameDir) {
  fs.mkdirSync(frameDir, { recursive: true });
  const totalFrames = Math.max(2, Math.round(scene.duration * FPS));
  console.log(`Rendering ${scene.id} (${scene.duration.toFixed(2)}s, ${totalFrames} frames)...`);

  const capturedFrames = [];

  async function snap() {
    const frameIndex = capturedFrames.length + 1;
    const framePath = path.join(frameDir, `raw_${String(frameIndex).padStart(4, '0')}.jpg`);
    await page.screenshot({ path: framePath, type: 'jpeg', quality: 85 });
    capturedFrames.push(framePath);
  }

  if (scene.id === 'scene1_intro') {
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2' });
    await sleep(1000);
    // 16.27s: smooth scroll down 700px, pause, scroll back
    const steps = 18;
    for (let i = 0; i < steps; i++) {
      if (i < 8) {
        await page.evaluate((scrollStep) => window.scrollBy(0, scrollStep), 60);
      } else if (i < 13) {
        // pause at features section
      } else {
        await page.evaluate((scrollStep) => window.scrollBy(0, scrollStep), -96);
      }
      await sleep(250);
      await snap();
    }
  } else if (scene.id === 'scene2_marketplace') {
    await page.goto('http://localhost:5173/?demo=true', { waitUntil: 'networkidle2' });
    await sleep(1000);
    await snap();

    // Hover and click on campaign card
    const card = await page.$('.border-hairline');
    await snap();
    
    // Click on campaign card or view details
    await page.evaluate(() => {
      const cards = document.querySelectorAll('div, button');
      for (const el of cards) {
        if (el.textContent && el.textContent.includes('Test Campaign')) {
          el.click();
          break;
        }
      }
    });
    await sleep(800);
    await snap();

    // Scroll inside modal if open
    const steps = 18;
    for (let i = 0; i < steps; i++) {
      if (i > 4 && i < 12) {
        await page.evaluate(() => {
          const modal = document.querySelector('.overflow-y-auto, [role="dialog"], .fixed');
          if (modal) modal.scrollBy(0, 40);
        });
      }
      await sleep(250);
      await snap();
    }
  } else if (scene.id === 'scene3_create_campaign') {
    await page.goto('http://localhost:5173/?demo=true', { waitUntil: 'networkidle2' });
    await sleep(800);
    await snap();

    // Click Create Campaign button
    await page.evaluate(() => {
      const btn = document.querySelector('#btn-open-create-modal') || Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Create Campaign'));
      if (btn) btn.click();
    });
    await sleep(800);
    await snap();

    // Fill in inputs in modal
    await page.evaluate(() => {
      const titleInput = document.querySelector('input[placeholder*="Title"], input[placeholder*="title"], #campaign-title') || document.querySelectorAll('input[type="text"]')[0];
      if (titleInput) {
        titleInput.value = 'Agent Tank — AI Marketing Pact';
        titleInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
      const budgetInput = document.querySelector('input[placeholder*="Budget"], input[type="number"], #campaign-budget');
      if (budgetInput) {
        budgetInput.value = '2.5';
        budgetInput.dispatchEvent(new Event('input', { bubbles: true }));
      }
    });
    await sleep(500);
    await snap();

    const steps = 15;
    for (let i = 0; i < steps; i++) {
      if (i === 4) {
        await page.evaluate(() => {
          const descInput = document.querySelector('textarea');
          if (descInput) {
            descInput.value = 'Autonomous influencer campaign verified by GenLayer multi-LLM consensus and milestone escrow.';
            descInput.dispatchEvent(new Event('input', { bubbles: true }));
          }
        });
      }
      await sleep(250);
      await snap();
    }
  } else if (scene.id === 'scene4_creator_reputation') {
    await page.goto('http://localhost:5173/?demo=true', { waitUntil: 'networkidle2' });
    await sleep(800);
    await snap();

    // Click X Profile / Connect X button
    await page.evaluate(() => {
      const btn = document.querySelector('#btn-dashboard-x-profile') || document.querySelector('#btn-nav-x-profile') || document.querySelector('#btn-nav-connect-x') || Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('𝕏'));
      if (btn) btn.click();
    });
    await sleep(800);
    await snap();

    const steps = 18;
    for (let i = 0; i < steps; i++) {
      await sleep(250);
      await snap();
    }
  } else if (scene.id === 'scene5_ai_consensus') {
    await page.goto('http://localhost:5173/about.html', { waitUntil: 'networkidle2' });
    await sleep(1000);
    await snap();

    // Smooth scroll down the 4 steps
    const steps = 22;
    for (let i = 0; i < steps; i++) {
      await page.evaluate(() => window.scrollBy(0, 95));
      await sleep(250);
      await snap();
    }
  } else if (scene.id === 'scene6_conclusion') {
    await page.goto('http://localhost:5173/?demo=true', { waitUntil: 'networkidle2' });
    await sleep(1000);
    await snap();

    const steps = 12;
    for (let i = 0; i < steps; i++) {
      if (i > 3 && i < 8) {
        await page.evaluate(() => window.scrollBy(0, 30));
      }
      await sleep(250);
      await snap();
    }
  }

  // Duplicate captured frames evenly to fill totalFrames
  console.log(`Captured ${capturedFrames.length} keyframes for ${scene.id}. Expanding to ${totalFrames} frames...`);
  const finalDir = path.join(frameDir, 'final');
  fs.mkdirSync(finalDir, { recursive: true });

  for (let f = 0; f < totalFrames; f++) {
    const srcIndex = Math.min(
      Math.floor((f / totalFrames) * capturedFrames.length),
      capturedFrames.length - 1
    );
    const srcFile = capturedFrames[srcIndex];
    const dstFile = path.join(finalDir, `frame_${String(f + 1).padStart(5, '0')}.jpg`);
    fs.copyFileSync(srcFile, dstFile);
  }

  return { totalFrames, finalDir };
}

async function main() {
  console.log('Launching headless Chrome for demo recording...');
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/google-chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1920,1080']
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });

  const sceneVideoFiles = [];

  for (const scene of scenes) {
    const frameDir = path.join('demo_assets', scene.id);
    const { totalFrames, finalDir } = await renderSceneFrames(page, scene, frameDir);

    const videoOut = path.join('demo_assets', `${scene.id}.mp4`);
    console.log(`Encoding ${scene.id}.mp4 with audio (${scene.file})...`);

    const ffmpegCmd = [
      '/home/michael/.local/bin/ffmpeg', '-y',
      '-framerate', String(FPS),
      '-i', path.join(finalDir, 'frame_%05d.jpg'),
      '-i', scene.file,
      '-c:v', 'libx264',
      '-pix_fmt', 'yuv420p',
      '-c:a', 'aac',
      '-shortest',
      videoOut
    ].join(' ');

    execSync(ffmpegCmd);
    console.log(`Successfully generated ${videoOut}! Size: ${fs.statSync(videoOut).size} bytes`);
    sceneVideoFiles.push(videoOut);
  }

  await browser.close();

  // Create concat file for ffmpeg
  const concatList = path.join('demo_assets', 'concat_list.txt');
  const fileLines = sceneVideoFiles.map(f => `file '${path.resolve(f)}'`).join('\n');
  fs.writeFileSync(concatList, fileLines);

  console.log('Concatenating all scenes into final video...');
  const finalVideo = path.resolve('adpact_agent_tank_demo.mp4');
  const concatCmd = [
    '/home/michael/.local/bin/ffmpeg', '-y',
    '-f', 'concat',
    '-safe', '0',
    '-i', concatList,
    '-c', 'copy',
    finalVideo
  ].join(' ');

  execSync(concatCmd);
  console.log(`\n🎉 FINAL DEMO VIDEO READY! 🎉`);
  console.log(`Path: ${finalVideo}`);
  console.log(`File Size: ${(fs.statSync(finalVideo).size / 1024 / 1024).toFixed(2)} MB`);
}

main().catch(err => {
  console.error('Error rendering demo video:', err);
  process.exit(1);
});
