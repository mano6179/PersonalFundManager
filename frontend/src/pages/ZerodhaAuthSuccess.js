import { useEffect } from 'react';

const ZerodhaAuthSuccess = () => {
  useEffect(() => {
    if (window.opener) {
      window.opener.postMessage({ type: 'ZERODHA_AUTH_SUCCESS' }, '*');
      window.close();
    }
  }, []);
  return <div>Authentication successful! You can close this window.</div>;
};

export default ZerodhaAuthSuccess;
