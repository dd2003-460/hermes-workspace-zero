import React from 'react';
import {Composition} from 'remotion';
import {Video} from './Video';

const FPS = 30;
const TOTAL_SEC = 118; // timeline total 117.83，取整
export const ROOT_DURATION = TOTAL_SEC * FPS;

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="video"
      component={Video}
      durationInFrames={ROOT_DURATION}
      fps={FPS}
      width={1280}
      height={720}
    />
  );
};
