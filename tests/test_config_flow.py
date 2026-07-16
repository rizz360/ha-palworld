"""Tests for the Palworld config and options flows."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.palworld.api import (
    PalworldApiError,
    PalworldAuthError,
    PalworldConnectionError,
)
from custom_components.palworld.const import CONF_SCAN_INTERVAL, DOMAIN

from .conftest import MOCK_DATA, MOCK_INFO


async def test_user_flow_success(hass):
    with patch(
        "custom_components.palworld.config_flow.PalworldClient.async_validate",
        return_value=MOCK_INFO,
    ), patch("custom_components.palworld.async_setup_entry", return_value=True):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], MOCK_DATA
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == MOCK_INFO["servername"]
    assert result2["data"] == MOCK_DATA


async def test_user_flow_title_falls_back_to_host(hass):
    with patch(
        "custom_components.palworld.config_flow.PalworldClient.async_validate",
        return_value={"version": "v1.5.0"},
    ), patch("custom_components.palworld.async_setup_entry", return_value=True):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], MOCK_DATA
        )
        await hass.async_block_till_done()

    assert result2["title"] == f"Palworld ({MOCK_DATA['host']})"


@pytest.mark.parametrize(
    ("side_effect", "expected_error"),
    [
        (PalworldAuthError(), "invalid_auth"),
        (PalworldConnectionError(), "cannot_connect"),
        (PalworldApiError(), "unknown"),
        (ValueError(), "unknown"),
    ],
)
async def test_user_flow_errors(hass, side_effect, expected_error):
    with patch(
        "custom_components.palworld.config_flow.PalworldClient.async_validate",
        side_effect=side_effect,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], MOCK_DATA
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": expected_error}


async def test_user_flow_duplicate_entry_aborts(hass, mock_config_entry):
    mock_config_entry.add_to_hass(hass)

    with patch(
        "custom_components.palworld.config_flow.PalworldClient.async_validate",
        return_value=MOCK_INFO,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], MOCK_DATA
        )

    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "already_configured"


async def test_options_flow_updates_scan_interval(hass, mock_config_entry):
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_SCAN_INTERVAL: 45}
    )

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["data"] == {CONF_SCAN_INTERVAL: 45}


async def test_reauth_flow_success(hass, mock_config_entry):
    mock_config_entry.add_to_hass(hass)

    result = await mock_config_entry.start_reauth_flow(hass)
    assert result["step_id"] == "reauth_confirm"

    with patch(
        "custom_components.palworld.config_flow.PalworldClient.async_validate",
        return_value=MOCK_INFO,
    ), patch("custom_components.palworld.async_setup_entry", return_value=True):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"password": "newpass"}
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "reauth_successful"
    assert mock_config_entry.data["password"] == "newpass"


async def test_reauth_flow_invalid_auth(hass, mock_config_entry):
    mock_config_entry.add_to_hass(hass)
    result = await mock_config_entry.start_reauth_flow(hass)

    with patch(
        "custom_components.palworld.config_flow.PalworldClient.async_validate",
        side_effect=PalworldAuthError(),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"password": "wrong"}
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["step_id"] == "reauth_confirm"
    assert result2["errors"] == {"base": "invalid_auth"}
