/**
 * Author: Utkarsh Gupta
 * License: GPL v3
 *
 * How a catalogue method's verification status is shown (form header, calculation cards). Only a known issue is
 * shown, as a warning; "verified" and "corrected" are internal QA states (benchmarks, wrapper fixes) and show
 * nothing, like "unverified".
 */
import { AlertTriangle } from 'lucide-react';

export const CALC_STATUS = {
    known_issue: { label: 'Known issue', className: 'text-error', Icon: AlertTriangle },
};
