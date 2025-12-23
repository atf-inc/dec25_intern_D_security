/* frontend/app/icon.tsx */
import { ImageResponse } from 'next/og';

// Image metadata
export const size = {
  width: 32,
  height: 32,
};
export const contentType = 'image/png';

// Image generation
export default function Icon() {
  return new ImageResponse(
    (
      // ImageResponse JSX element
      <div
        style={{
          fontSize: 20,
          background: '#030303', // Your bg-DEFAULT color
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#00F0FF', // Your accent-cyan color
          borderRadius: '4px',
          border: '1px solid #333',
        }}
      >
        🛡️
      </div>
    ),
    // ImageResponse options
    {
      ...size,
    }
  );
}