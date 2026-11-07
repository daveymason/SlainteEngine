import React from 'react';
import SecurityRoundedIcon from '@mui/icons-material/SecurityRounded';
import VerifiedUserRoundedIcon from '@mui/icons-material/VerifiedUserRounded';
import BugReportRoundedIcon from '@mui/icons-material/BugReportRounded';
import PrivacyTipRoundedIcon from '@mui/icons-material/PrivacyTipRounded';
import FactCheckRoundedIcon from '@mui/icons-material/FactCheckRounded';
import SyncAltRoundedIcon from '@mui/icons-material/SyncAltRounded';
import SummarizeRoundedIcon from '@mui/icons-material/SummarizeRounded';
import MedicationLiquidRoundedIcon from '@mui/icons-material/MedicationLiquidRounded';
import MonitorHeartRoundedIcon from '@mui/icons-material/MonitorHeartRounded';
import MicRoundedIcon from '@mui/icons-material/MicRounded';
import InsightsRoundedIcon from '@mui/icons-material/InsightsRounded';
import type { SvgIconProps } from '@mui/material/SvgIcon';
import type { AgentCapability } from '@/data/agentsData';

export function AgentIcon({
  iconKey,
  ...props
}: { iconKey: AgentCapability['iconKey'] } & SvgIconProps) {
  switch (iconKey) {
    case 'security':
      return <SecurityRoundedIcon aria-hidden="true" {...props} />;
    case 'verified':
      return <VerifiedUserRoundedIcon aria-hidden="true" {...props} />;
    case 'bug':
      return <BugReportRoundedIcon aria-hidden="true" {...props} />;
    case 'privacy':
      return <PrivacyTipRoundedIcon aria-hidden="true" {...props} />;
    case 'factCheck':
      return <FactCheckRoundedIcon aria-hidden="true" {...props} />;
    case 'sync':
      return <SyncAltRoundedIcon aria-hidden="true" {...props} />;
    case 'summarize':
      return <SummarizeRoundedIcon aria-hidden="true" {...props} />;
    case 'medication':
      return <MedicationLiquidRoundedIcon aria-hidden="true" {...props} />;
    case 'monitorHeart':
      return <MonitorHeartRoundedIcon aria-hidden="true" {...props} />;
    case 'mic':
      return <MicRoundedIcon aria-hidden="true" {...props} />;
    case 'analytics':
      return <InsightsRoundedIcon aria-hidden="true" {...props} />;
  }
}
